#-*- encoding: utf-8 -*-

import json
import urllib2
from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase
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
        self.graph = facebook.GraphAPI(access_token=self.jsonconf['access_token'])

    @staticmethod
    def new_channel(full=False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'FacebookFeed'
        c['access_token'] = ''
        c['app_id'] = ''
        c['app_key'] = ''

        return c

    def read_channel(self, channel):
        super(FacebookFeed, self).read_channel(channel)

    def auth(self):
        logger.info("Current implementation of Facebook does not use auth!")

    def home_timeline(self, count=20):
        status_list = snstype.MessageList()
        try:
            statuses = self.graph.get_connections("me", "home")
            while True:
                for s in statuses['data']:
                    if len(status_list) >= count:
                        break
                    status_list.append(self.Message(s,\
                            self.jsonconf['platform'],\
                            self.jsonconf['channel_name']))
                if len(status_list) >= count:
                    break
                logger.debug('reading next page')
                t = urllib2.urlopen(statuses['paging']['next'] + '&access_token=' + self.jsonconf['access_token'])
                statuses = json.loads(t.read())
        except Exception, e:
            logger.warning("Catch expection: %s", e)
        return status_list

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

    def is_authed(self, token=None):
        if token == None:
            token = self.jsonconf['access_token']
        t = facebook.GraphAPI(access_token=token)
        res = t.request('me/')
        if 'error' in res:
            return False
        else:
            if self.jsonconf['app_secret'] and self.jsonconf['app_id']:
                res = t.extend_access_token(self.jsonconf['app_id'], self.jsonconf['app_secret'])
                self.graph.access_token = res['access_token']
            return True

    def expire_after(self, token = None):
        # This platform does not have token expire issue.
        if self.is_authed():
            return -1
        else:
            return 0
