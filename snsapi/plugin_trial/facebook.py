#-*- encoding: utf-8 -*-

import time
import re
from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase, require_authed
from .. import snstype
from .. import utils

from ..third import facebook

logger.debug("%s plugged!", __file__)

class FacebookFeedMessage(snstype.Message):
    platform = "FacebookFeed"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.id = dct['id']

        self.parsed.time = utils.str2utc(dct['created_time'])
        self.parsed.username = dct['from']['name']
        self.parsed.userid = dct['from']['id']
        self.parsed.attachments = []
        resmsg = []
        if 'message' in dct:
            resmsg.append(dct['message'])
        if 'story' in dct:
            resmsg.append(dct['story'])
        if dct['type'] == 'photo':
            self.parsed.attachments.append({
                'type': 'picture',
                'format': ['link'],
                #NOTE: replace _s to _n will get the original picture
                'data': re.sub(r'_[a-z](\.[^.]*)$', r'_n\1', dct['picture'])
            })
        if dct['type'] == 'video':
            self.parsed.attachments.append({
                'type': 'video',
                'format': ['link'],
                'data': dct['link']
            })
        if dct['type'] == 'link':
            self.parsed.attachments.append({
                'type': 'link',
                'format': ['link'],
                'data': dct['link']
            })
        self.parsed.text = '\n'.join(resmsg)


class FacebookFeed(SNSBase):

    Message = FacebookFeedMessage

    def __init__(self, channel=None):
        super(FacebookFeed, self).__init__(channel)
        self.platform = self.__class__.__name__
        self.token = {}

    @staticmethod
    def new_channel(full=False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'FacebookFeed'
        c['access_token'] = ''
        # The client_id in FB's term
        c['app_key'] = ''
        c['app_secret'] = ''

        c['auth_info'] = {
                "save_token_file": "(default)",
                "cmd_request_url": "(default)",
                "callback_url": "http://snsapi.ie.cuhk.edu.hk/aux/auth.php",
                "cmd_fetch_code": "(default)"
                }

        return c

    def read_channel(self, channel):
        super(FacebookFeed, self).read_channel(channel)

    def auth_first(self):
        url = "https://www.facebook.com/dialog/oauth?client_id=" + \
                self.jsonconf['app_key'] + \
                "&redirect_uri=" + \
                self.auth_info['callback_url'] + \
                "&response_type=token&scope=read_stream,publish_stream"
        self.request_url(url)

    def auth_second(self):
        #TODO:
        #    Find a way to get the code in parameters, not in URL fragmentation
        try:
            url = self.fetch_code()
            url = url.replace('#', '?')
            self.token = self._parse_code(url)
            self.token.expires_in = int(int(self.token.expires_in) + time.time())
            #self.token = {'access_token' : self.fetch_code(),
            #              'expires_in' : -1}
            self.graph = facebook.GraphAPI(access_token=self.token['access_token'])
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None

    def _do_oauth(self):
        '''
        The two-stage OAuth
        '''
        self.auth_first()
        self.auth_second()
        if self._is_authed():
            self.save_token()
            return True
        else:
            logger.info("OAuth channel '%s' on Facebook fail", self.jsonconf.channel_name)
            return False


    def auth(self):
        if self.get_saved_token():
            self.graph = facebook.GraphAPI(access_token=self.token['access_token'])
            return True
        if self.jsonconf['access_token'] and self._is_authed(self.jsonconf['access_token']):
            self.token = {'access_token': self.jsonconf['access_token'], 'expires_in' : -1}
            self.graph = facebook.GraphAPI(access_token=self.token['access_token'])
            self.save_token()
            return True
        elif 'access_token' not in self.jsonconf or not self.jsonconf['access_token']:
            return self._do_oauth()
        else:
            logger.debug('auth failed')
            return False

    @require_authed
    def home_timeline(self, count=20):
        status_list = snstype.MessageList()
        statuses = self.graph.get_connections("me", "home", limit=count)
        for s in statuses['data']:
            try:
                status_list.append(self.Message(s,\
                        self.jsonconf['platform'],\
                        self.jsonconf['channel_name']))
            except Exception, e:
                logger.warning("Catch expection: %s", e)
        logger.info("Read %d statuses from '%s'", len(status_list), self.jsonconf['channel_name'])
        return status_list

    @require_authed
    def update(self, text):
        try:
            status = self.graph.put_object("me", "feed", message=self._unicode_encode(text))
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Facebook failed: %s', str(e))
            return False

    @require_authed
    def reply(self, statusID, text):
        try:
            status = self.graph.put_object(statusID.id, "comments", message=self._unicode_encode(text))
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning("commenting on Facebook failed:%s", str(e))
            return False

    def need_auth(self):
        return True

    def _is_authed(self, token=None):
        #FIXME:
        #TODO:
        #    Important refactor point here!
        #    See `SNSBase.expire_after` for the flow.
        #    The aux function should only look at the 'token' parameter.
        #    Belowing is just a logic fix.
        orig_token = token
        if token == None:
            if self.token and 'access_token' in self.token:
                token = self.token['access_token']
            else:
                # No token passed in. No token in `self.token`
                # --> not authed
                return False
        t = facebook.GraphAPI(access_token=token)
        try:
            res = t.request('me/')
            if orig_token == None and self.token and self.jsonconf['app_secret'] and self.jsonconf['app_key'] and (self.token['expires_in'] - time.time() < 6000):
                logger.debug("refreshing token")
                try:
                    res = t.extend_access_token(self.jsonconf['app_key'], self.jsonconf['app_secret'])
                    print res
                    logger.debug("new token expires in %s relative seconds" % (res['expires']))
                    self.token['access_token'] = res['access_token']
                    if 'expires' in res:
                        self.token['expires_in'] = int(res['expires']) + time.time()
                    else:
                        #TODO:
                        #    How to come to this branch?
                        #    Can we assert False here?
                        self.token['expires_in'] = -1
                    self.graph.access_token = res['access_token']
                    self.save_token()
                except Exception, ei:
                    logger.warning("Refreshing token failed: %s", ei)
                    return False
            return True
        except Exception, e:
            logger.warning("Catch Exception: %s", e)
            return False

    def expire_after(self, token = None):
        # This platform does not have token expire issue.
        if token and 'access_token' in token:
            token = token['access_token']
        else:
            token = None
        if self._is_authed(token):
            if 'expires_in' in self.token:
                return self.token['expires_in'] - time.time()
            else:
                return -1
        else:
            return 0
