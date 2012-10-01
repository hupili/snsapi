# -*- coding: utf-8 -*-

'''
snspocket: the container class for snsapi's

'''

# === system imports ===
try:
    import json
except ImportError:
    import simplejson as json
from os.path import abspath

# === snsapi modules ===
import snstype
import utils
from errors import snserror
from utils import JsonDict
from utils import console_output
from snslog import SNSLog
logger = SNSLog
import platform

# === 3rd party modules ===

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
        #    'snsapi'?
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
            self[cname] = p(jsonconf)
            #TODO:
            #    This is a work around to store rich 
            #    channel information in the snsapi 
            #    class. The snsapi class should be 
            #    upgrade so that jsonconf is its 
            #    default entrance to access all 
            #    config matters. The current hard 
            #    code attributes are not friendly to
            #    upgrades. Say you have to write one
            #    more assignment if there is one more 
            #    config entry. e.g.
            #    self.open = channel['open']
            self[cname].jsonconf = jsonconf
            self.__method_routing(cname, SNSPocket.__default_mapping) 
        except AttributeError:
            logger.warning("No such platform '%s'. Nothing happens to it. ", jsonconf['platform'])

        return True

    def load_config(self, \
            fn_channel = 'conf/channel.json',\
            fn_pocket = 'conf/pocket.json'):
        """
        Read configs:
        * channel.conf
        * pocket.conf
        """

        count_add_channel = 0 
        try:
            with open(abspath(fn_channel), "r") as fp:
                allinfo = json.load(fp)
                for site in allinfo:
                    if self.add_channel(JsonDict(site)):
                        count_add_channel += 1
        except IOError:
            raise snserror.config.nofile(fn_channel)

        try:
            with open(abspath(fn_pocket), "r") as fp:
                allinfo = json.load(fp)
                self.jsonconf = allinfo
        except IOError:
            raise snserror.config.nofile(fn_pocket)

        logger.info("Read configs done. Add %d channels" % count_add_channel)

    def save_config(self, \
            fn_channel = 'conf/channel.json',\
            fn_pocket = 'conf/pocket.json'):
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

    def new_channel(self):
        return JsonDict(json.load(open(abspath('conf/init-channel.json.example'),'r')))   

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
            self[c].auth()
        else:
            for c in self.itervalues():
                c.auth()

    def home_timeline(self, count = 20, channel = None):
        """
        Route to home_timeline method of snsapi. 
        
        :param channel:
            The channel name. Use None to read all channels
        """
        status_list = snstype.StatusList()
        if channel:
            status_list.extend(self[channel].home_timeline(count))
        else:
            for c in self.itervalues():
                if c.jsonconf['open'] == "yes":
                    status_list.extend(c.home_timeline(count))

        logger.info("Read %d statuses", len(status_list))
        return status_list

    def update(self, text, channel = None):
        """
        Route to update method of snsapi. 
        
        :param channel:
            The channel name. Use None to update all channels
        """
        re = {}
        if channel:
            re[channel] = self[channel].update(text)
        else:
            for c in self.itervalues():
                if c.jsonconf['open'] == "yes":
                    re[c.jsonconf['channel_name']] = c.update(text)

        logger.info("Update status '%s'. Result:%s", text, re)
        return re

    def reply(self, statusID, text, channel = None):
        """
        Route to reply method of snsapi. 
        
        :param channel:
            The channel name. Use None to automatically select
            one compatible channel. 
        """
        re = {}
        if channel:
            re = self[channel].reply(statusID, text)
        else:
            for c in self.itervalues():
                if c.jsonconf['open'] == "yes":
                    if c.jsonconf['platform'] == statusID.platform:
                        re = c.reply(statusID, text)
                        break

        logger.info("Reply to status '%s' with text '%s'. Result: %s",\
                statusID, text, re)
        return re
