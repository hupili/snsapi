# -*- coding: utf-8 -*-

'''
snspocket: the container class for snsapi's

'''

# === system imports ===
from utils import json
from os import path
import sqlite3
import thread

# === snsapi modules ===
import snstype
import utils
from errors import snserror
from utils import console_output, obj2str, str2obj
from snslog import SNSLog as logger
from snsconf import SNSConf
import platform
from async import AsyncDaemonWithCallBack

# === 3rd party modules ===

DIR_DEFAULT_CONF_CHANNEL = path.join(SNSConf.SNSAPI_DIR_STORAGE_CONF, 'channel.json')
DIR_DEFAULT_CONF_POCKET = path.join(SNSConf.SNSAPI_DIR_STORAGE_CONF, 'pocket.json')


def _default_callback(pocket, res):
    pass

class BackgroundOperationPocketWithSQLite:
    def __init__(self, pocket, sqlite, callback=_default_callback, timeline_sleep=60, update_sleep=10):
        self.sp = pocket
        self.dblock = thread.allocate_lock()
        self.sqlitefile = sqlite
        conn = sqlite3.connect(self.sqlitefile)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS home_timeline (
            id integer primary key, pickled_object text, digest text, text text, username text, userid text, time integer, isread integer DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS pending_update (
            id integer primary key, callback text, type text, args text, kwargs text
        )""")
        conn.commit()
        c.close()
        self.home_timeline_job = AsyncDaemonWithCallBack(self.sp.home_timeline, (), {}, self.write_timeline_to_db, timeline_sleep)
        self.update_job = AsyncDaemonWithCallBack(self.update_func, (), {}, None, update_sleep)
        self.home_timeline_job.start()
        self.update_job.start()

    def home_timeline(self, count=20):
        ret = snstype.MessageList()
        logger.debug("acquiring lock")
        self.dblock.acquire()
        try:
            conn = sqlite3.connect(self.sqlitefile)
            c = conn.cursor()
            c.execute("SELECT pickled_object FROM home_timeline ORDER BY time DESC LIMIT 0, %d" % (count,))
            p = c.fetchall()
            logger.info("%d messages read from database" % (len(p)))
            for i in p:
                ret.append(str2obj(str(i[0])))
        except Exception, e:
            logger.warning("Error while reading database: %s" % (str(e)))
        finally:
            logger.debug("releasing lock")
            self.dblock.release()
            return ret

    def write_timeline_to_db(self, msglist):
        logger.debug("acquiring lock")
        self.dblock.acquire()
        try:
            conn = sqlite3.connect(self.sqlitefile)
            cursor = conn.cursor()
            what_to_write = [
            ]
            for msg in msglist:
                try:
                    pickled_msg = obj2str(msg)
                    sig = unicode(msg.digest())
                    cursor.execute("SELECT * FROM home_timeline WHERE digest = ?", (sig,))
                    if not cursor.fetchone():
                        what_to_write.append((
                            unicode(pickled_msg), sig, msg.parsed.text, msg.parsed.username, msg.parsed.userid, msg.parsed.time
                        ))
                except Exception, e:
                    logger.warning("Error while checking message: %s" % (str(e)))
            try:
                logger.info("Writing %d messages" % (len(what_to_write)))
                cursor.executemany("INSERT INTO home_timeline (pickled_object, digest, text, username, userid, time) VALUES(?, ?, ?, ?, ?, ?)", what_to_write)
            except Exception, e:
                logger.warning("Error %s" % (str(e)))
            conn.commit()
            cursor.close()
        finally:
            logger.debug("releasing lock")
            self.dblock.release()

    def _update(self, type, args, kwargs):
        logger.debug("acquiring lock")
        self.dblock.acquire()
        try:
            conn = sqlite3.connect(self.sqlitefile)
            cursor = conn.cursor()
            callback = None
            if 'callback' in kwargs:
                callback = kwargs['callback']
                del kwargs['callback']
            cursor.execute("INSERT INTO pending_update (type, callback, args, kwargs) VALUES (?, ?, ?, ?)", (
                type,
                obj2str(callback),
                obj2str(args),
                obj2str(kwargs)
            ))
            conn.commit()
            cursor.close()
            return True
        except Exception, e:
            logger.warning("Error while saving pending_update: %s" % (str(e)))
            return False
        finally:
            logger.debug("releasing lock")
            self.dblock.release()

    def update(self, *args, **kwargs):
        return self._update('update', args, kwargs)

    def forward(self, *args, **kwargs):
        return self._update('forward', args, kwargs)

    def reply(self, *args, **kwargs):
        return self._update('reply', args, kwargs)

    def update_func(self):
        logger.debug("acquiring lock")
        self.dblock.acquire()
        try:
            conn = sqlite3.connect(self.sqlitefile)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pending_update")
            i = cursor.fetchone()
            if i:
                cursor.execute("DELETE FROM pending_update WHERE id = ?", (i['id'], ))
                j = {
                    'id': str(i['id']),
                    'args': str2obj(str(i['args'])),
                    'kwargs': str2obj(str(i['kwargs'])),
                    'type': str(i['type']),
                    'callback': str2obj(str(i['callback']))
                }
                res = getattr(self.sp, j['type'])(*j['args'], **j['kwargs'])
                if j['callback']:
                    j['callback'](self, res)
            conn.commit()
            cursor.close()
        except Exception, e:
            logger.warning("Error while updating: %s" % (str(e)))
        finally:
            logger.debug("releasing lock")
            self.dblock.release()


class SNSPocket(dict):
    """The container class for snsapi's"""

    __default_mapping = {
        "home_timeline" : "home_timeline",
        "update" : "update",
        "reply" : "reply",
        "read" : "home_timeline",
        "write" : "update",
        "writeto" : "reply"}

    def __init__(self):
        super(SNSPocket, self).__init__()
        self.jsonconf = {}

    def __iter__(self):
        """
        By default, the iterator only return opened channels.
        """
        l = []
        for c in self.itervalues():
            if c.jsonconf['open'] == 'yes':
                l.append(c.jsonconf['channel_name'])
        return iter(l)

    def clear_channel(self):
        self.clear()

    def __dummy_method(self, channel, name):

        def dummy(*al, **ad):
            logger.warning("'%s' does not have method '%s'", channel, name)
            return False

        return dummy

    def __method_routing(self, channel, mapping = None):
        #TODO:
        #    This function can support higher layer method
        #    routing. The basic usage is to enable alias to
        #    lower level methods. e.g. you can call "read",
        #    which may be routed to "home_timeline" for
        #    real business.
        #
        #    Currently, it is here to map non existing methods
        #    to dummy methods.
        #
        #    It's also unclear that where is the best place
        #    for this function. here, or in the base class
        #    'SNSBase'?
        #
        #    The implementation does not look good.
        #    I need two scan:
        #       * The first is to determine who is dummy.
        #       * The second is to really assign dummy.
        #
        #    If we do everything in one scan, after assigning
        #    dummy, the later reference will find it "hasattr".
        #    Then we do not get the correct method name in
        #    log message.

        if not mapping:
            mapping = SNSPocket.__default_mapping

        c = self[channel]
        d = {}

        for src in mapping:
            dst = mapping[src]
            if not hasattr(c, dst):
                d[dst] = 1
                d[src] = 1
            else :
                if src != dst:
                    setattr(c, src, getattr(c,dst))

        for m in d:
            setattr(c, m, self.__dummy_method(channel, m))

    def add_channel(self, jsonconf):
        logger.debug(json.dumps(jsonconf))
        cname = jsonconf['channel_name']

        if cname in self:
            logger.warning("Duplicate channel_name '%s'. Nothing happens to it. ", cname)
            return False

        try:
            p = getattr(platform, jsonconf['platform'])
        except AttributeError:
            p = None
            logger.warning("No such platform '%s'. Nothing happens to it. ", jsonconf['platform'])
            return False
        if p:
            self[cname] = p(jsonconf)
            self.__method_routing(cname, SNSPocket.__default_mapping)

        return True

    def load_config(self,
            fn_channel = DIR_DEFAULT_CONF_CHANNEL,
            fn_pocket = DIR_DEFAULT_CONF_POCKET):
        """
        Read configs:
        * channel.conf
        * pocket.conf
        """

        count_add_channel = 0
        try:
            with open(path.abspath(fn_channel), "r") as fp:
                allinfo = json.load(fp)
                for site in allinfo:
                    if self.add_channel(utils.JsonDict(site)):
                        count_add_channel += 1
        except IOError:
            #raise snserror.config.nofile(fn_channel)
            logger.warning("'%s' does not exist. Use default", fn_channel)
        except ValueError as e:
            raise snserror.config.load("file: %s; message: %s" % (fn_channel, e))

        try:
            with open(path.abspath(fn_pocket), "r") as fp:
                allinfo = json.load(fp)
                self.jsonconf = allinfo
        except IOError:
            #raise snserror.config.nofile(fn_pocket)
            logger.warning("'%s' does not exist. Use default", fn_pocket)
        except ValueError as e:
            raise snserror.config.load("file: %s; message:%s" % (fn_channel, e))

        logger.info("Read configs done. Add %d channels" % count_add_channel)

    def save_config(self,
            fn_channel = DIR_DEFAULT_CONF_CHANNEL,
            fn_pocket = DIR_DEFAULT_CONF_POCKET):
        """
        Save configs: reverse of load_config

        Configs can be modified during execution. snsapi components
        communicate with upper layer using Python objects. Pocket
        will be the unified place to handle file transactions.

        """

        conf_channel = []
        for c in self.itervalues():
            conf_channel.append(c.jsonconf)

        conf_pocket = self.jsonconf

        try:
            json.dump(conf_channel, open(fn_channel, "w"), indent = 2)
            json.dump(conf_pocket, open(fn_pocket, "w"), indent = 2)
        except:
            raise snserror.config.save

        logger.info("save configs done")

    def new_channel(self, pl = None, **kwarg):
        if pl:
            try:
                return getattr(platform, pl).new_channel(**kwarg)
            except AttributeError:
                logger.warning("can not find platform '%s'", pl)
                return utils.JsonDict()
        else:
            _fn_conf = path.join(SNSConf._SNSAPI_DIR_STATIC_DATA, 'init-channel.json.example')
            return utils.JsonDict(json.load(open(_fn_conf)))

    def list_platform(self):
        console_output("")
        console_output("Supported platforms:")
        for p in platform.platform_list:
            console_output("   * %s" % p)
        console_output("")


    def list_channel(self, channel = None, verbose = False):
        if channel:
            try:
                console_output(str(self[channel].jsonconf))
            except KeyError:
                logger.warning("No such channel '%s'.", channel)
        else:
            console_output("")
            console_output("Current channels:")
            for cname in self.iterkeys():
                c = self[cname].jsonconf
                console_output("   * %s: %s %s" % \
                        (c['channel_name'],c['platform'],c['open']))
                if verbose:
                    console_output("    %s" % json.dumps(c))
            console_output("")

    def auth(self, channel = None):
        """docstring for auth"""
        if channel:
            self[channel].auth()
        else:
            for c in self.itervalues():
                if self.__check_method(c, ''):
                    c.auth()

    def __check_method(self, channel, method):
        '''
        Check availability of batch operation methods:

           * First the channel 'open' is switched on.
           * There is no 'methods' fields meaning all
           methods can be invoked by default.
           * If there is methods, check whether the current
           method is defaultly enabled.

        '''
        if channel.jsonconf['open'] == "yes":
            if not 'methods' in channel.jsonconf:
                return True
            elif channel.jsonconf['methods'].find(method) != -1:
                return True
        return False

    def _home_timeline(self, count, ch):
        #TODO:
        #    The following set default parameter for home_timeline.
        #    Other methods may also need default parameter some time.
        #    We should seek for a more unified solution.
        #    e.g.
        #    When adding channels, hide their original function
        #    and substitue it with a partial evaluated version
        #    using configured defaults
        if not count:
            if 'home_timeline' in ch.jsonconf:
                count = ch.jsonconf['home_timeline']['count']
            else:
                count = 20
        return ch.home_timeline(count)

    def home_timeline(self, count = None, channel = None):
        """
        Route to home_timeline method of snsapi.

        :param channel:
            The channel name. Use None to read all channels
        """

        status_list = snstype.MessageList()
        if channel:
            if channel in self:
                if self[channel].is_expired():
                    logger.warning("channel '%s' is expired. Do nothing.", channel)
                else:
                    status_list.extend(self._home_timeline(count, self[channel]))
            else:
                logger.warning("channel '%s' is not in pocket. Do nothing.", channel)
        else:
            for c in self.itervalues():
                if self.__check_method(c, 'home_timeline') and not c.is_expired():
                    status_list.extend(self._home_timeline(count, c))

        logger.info("Read %d statuses", len(status_list))
        return status_list

    def update(self, text, channel = None, **kwargs):
        """
        Route to update method of snsapi.

        :param channel:
            The channel name. Use None to update all channels
        """
        re = {}
        if channel:
            if channel in self:
                if self[channel].is_expired():
                    logger.warning("channel '%s' is expired. Do nothing.", channel)
                else:
                    re[channel] = self[channel].update(text)
            else:
                logger.warning("channel '%s' is not in pocket. Do nothing.", channel)
        else:
            for c in self.itervalues():
                if self.__check_method(c, 'update') and not c.is_expired():
                    re[c.jsonconf['channel_name']] = c.update(text, **kwargs)

        logger.info("Update status '%s'. Result:%s", text, re)
        return re

    def reply(self, message, text, channel = None):
        """
        Route to reply method of snsapi.

        :param channel:
            The channel name. Use None to automatically select
            one compatible channel.

        :param status:
            Message or MessageID object.

        :text:
            Reply text.
        """

        if isinstance(message, snstype.Message):
            mID = message.ID
        elif isinstance(message, snstype.MessageID):
            mID = message
        else:
            logger.warning("unknown type: %s", type(message))
            return {}

        re = {}
        if channel:
            if channel in self:
                if self[channel].is_expired():
                    logger.warning("channel '%s' is expired. Do nothing.", channel)
                else:
                    re = self[channel].reply(mID, text)
            else:
                logger.warning("channel '%s' is not in pocket. Do nothing.", channel)
        else:
            for c in self.itervalues():
                if self.__check_method(c, 'reply') and not c.is_expired():
                    #TODO:
                    #    First try to match "channel_name".
                    #    If there is no match, try to match "platform".
                    if c.jsonconf['platform'] == mID.platform:
                        re = c.reply(mID, text)
                        break

        logger.info("Reply to status '%s' with text '%s'. Result: %s",\
                mID, text, re)
        return re

    def forward(self, message, text, channel = None):
        """
        forward a message

        """
        re = {}
        if channel:
            if channel in self:
                if self[channel].is_expired():
                    logger.warning("channel '%s' is expired. Do nothing.", channel)
                else:
                    re = self[channel].forward(message, text)
            else:
                logger.warning("channel '%s' is not in pocket. Do nothing.", channel)
        else:
            for c in self.itervalues():
                if self.__check_method(c, 'forward') and not c.is_expired():
                    re[c.jsonconf['channel_name']] = c.forward(message, text)

        logger.info("Forward status '%s' with text '%s'. Result: %s",\
                message.digest(), text, re)
        return re
