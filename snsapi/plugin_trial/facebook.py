#-*- encoding: utf-8 -*-

import json
import urllib2
import time
from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase, require_authed
from .. import snstype
from ..utils import console_output
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
        resmsg = []
        if 'message' in dct:
            resmsg.append(dct['message'])
        if 'story' in dct:
            resmsg.append(dct['story'])
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
        c['app_id'] = ''
        c['app_key'] = ''
        c['redirect_uri'] = ''

        return c

    def read_channel(self, channel):
        super(FacebookFeed, self).read_channel(channel)

    def _do_auth(self):
        url = "https://www.facebook.com/dialog/oauth?client_id=" + \
                self.jsonconf['app_id'] + \
                "&redirect_uri=" + \
                self.jsonconf['redirect_uri'] + \
                "&response_type=token&scope=read_stream,publish_stream"
        console_output("Please open " + url + '\n')
        console_output("Please input token: ")
        self.token = {'access_token' : self.console_input().strip(),
                      'expires' : -1}
        self.graph = facebook.GraphAPI(access_token=self.token['access_token'])
        if self._is_authed():
            self.save_token()

    def auth(self):
        #FIXME: This is not a real authentication, just refresh token, and save
        if self.get_saved_token():
            self.graph = facebook.GraphAPI(access_token=self.token['access_token'])
            return True
        if self.jsonconf['access_token'] and self._is_authed(self.jsonconf['access_token']):
            self.token = {'access_token': self.jsonconf['access_token'], 'expires' : -1}
            self.graph = facebook.GraphAPI(access_token=self.token['access_token'])
            self.save_token()
            return True
        elif 'access_token' not in self.jsonconf or not self.jsonconf['access_token']:
            self._do_auth()
        else:
            logger.debug('auth failed')
            return False

    @require_authed
    def home_timeline(self, count=20):
        status_list = snstype.MessageList()
        try:
            statuses = self.graph.get_connections("me", "home", limit=count)
            for s in statuses['data']:
                status_list.append(self.Message(s,\
                        self.jsonconf['platform'],\
                        self.jsonconf['channel_name']))
        except Exception, e:
            logger.warning("Catch expection: %s", e)
        return status_list

    @require_authed
    def update(self, text):
        try:
            status = self.graph.put_object("me", "feed", message=text)
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Facebook failed: %s', str(e))
            return False

    def _is_authed(self, token=None):
        orig_token = token
        if token == None and 'access_token' in self.token:
            token = self.token['access_token']
        t = facebook.GraphAPI(access_token=token)
        try:
            res = t.request('me/')
            if orig_token == None and self.jsonconf['app_secret'] and self.jsonconf['app_id'] and (self.token['expires'] - time.time() < 600):
                logger.debug("refreshing token")
                try:
                    res = t.extend_access_token(self.jsonconf['app_id'], self.jsonconf['app_secret'])
                    logger.debug("new token expires in %s" % (res['expires']))
                    self.token['access_token'] = res['access_token']
                    if 'expires' in res:
                        self.token['expires'] = int(res['expires']) + time.time()
                    else:
                        self.token['expires'] = -1
                    self.graph.access_token = res['access_token']
                except Exception, ei:
                    logger.warning("Refreshing token failed: %s", ei)
            return True
        except:
            return False

    def expire_after(self, token = None):
        # This platform does not have token expire issue.
        if token and 'access_token' in token:
            token = token['access_token']
        else:
            token = None
        if self._is_authed(token):
            if 'expires' in self.token:
                return self.token['expires']
            else:
                return -1
        else:
            return 0
