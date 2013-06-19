#-*- encoding: utf-8 -*-

'''
twitter

We use python-twitter as the backend at present. 
It should be changed to invoke REST API directly later. 
'''

from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype
from ..utils import console_output
from .. import utils

from ..third import twitter

logger.debug("%s plugged!", __file__)

class TwitterStatusMessage(snstype.Message):
    platform = "TwitterStatus"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.id = dct['id']

        self.parsed.time = utils.str2utc(dct['created_at'])
        self.parsed.username = dct['user']['name']
        self.parsed.userid = dct['user']['id']
        self.parsed.text = dct['text']


class TwitterStatus(SNSBase):

    Message = TwitterStatusMessage

    def __init__(self, channel = None):
        super(TwitterStatus, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.api = twitter.Api(consumer_key=self.jsonconf['app_key'],\
                consumer_secret=self.jsonconf['app_secret'],\
                access_token_key=self.jsonconf['access_key'],\
                access_token_secret=self.jsonconf['access_secret'])


    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'TwitterStatus'
        c['app_key'] = ''
        c['app_secret'] = ''
        c['access_key'] = ''
        c['access_secret'] = ''

        return c
        
    def read_channel(self, channel):
        super(TwitterStatus, self).read_channel(channel) 

    def auth(self):
        logger.info("Current implementation of Twitter does not use auth!")

    def home_timeline(self, count = 20):
        status_list = snstype.MessageList()
        try:
            statuses = self.api.GetHomeTimeline(count = count)
            for s in statuses:
                status_list.append(self.Message(s.AsDict(),\
                        self.jsonconf['platform'],\
                        self.jsonconf['channel_name']))
        except Exception, e:
            logger.warning("Catch expection: %s", e)
        return status_list

    def update(self, text):
        text = self._cat(140, [(text, 1)])
        try:
            status = self.api.PostUpdate(text)
            #TODO:
            #     Find better indicator for status update success
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Twitter failed: %s', str(e))
            return False

    def expire_after(self, token = None):
        # This platform does not have token expire issue. 
        return -1
