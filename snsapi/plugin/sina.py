#-*- encoding: utf-8 -*-

'''
SINA micro-blog client
'''

from ..snslog import SNSLog 
logger = SNSLog
from ..snsapi import SNSAPI
from .. import snstype
from ..errors import snserror

logger.debug("%s plugged!", __file__)

class SinaWeiboStatus(SNSAPI):

    class Message(snstype.Status):
        def parse(self, dct):
            self.ID.platform = self.platform

            self.id = dct["id"]
            self.ID.id = self.id
            self.created_at = dct["created_at"]
            self.text = dct['text']
            self.reposts_count = dct['reposts_count']
            self.comments_count = dct['comments_count']
            self.username = dct['user']['name']
            self.usernick = ""


    def __init__(self, channel = None):
        super(SinaWeiboStatus, self).__init__()
        
        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

        #just you remind myself they exists
        self.app_key = ""
        self.app_secret = ""
        if channel:
            self.read_channel(channel)

    def read_channel(self, channel):
        super(SinaWeiboStatus, self).read_channel(channel) 

        self.channel_name = channel['channel_name']
        self.app_key = channel['app_key']
        self.app_secret = channel['app_secret']

        if not "auth_url" in self.auth_info:
            self.auth_info.auth_url = "https://api.weibo.com/oauth2/"
        if not "callback_url" in self.auth_info:
            self.auth_info.callback_url = "http://copy.the.code.to.client/"
        return 

    def auth_first(self):
        self._oauth2_first()

    def auth_second(self):
        self._oauth2_second()
        
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        url = "https://api.weibo.com/2/statuses/home_timeline.json"
        params = {}
        params['count'] = count
        params['access_token'] = self.token.access_token
        
        jsondict = self._http_get(url, params)
        
        if("error" in  jsondict):
            return [Error(jsondict),]
        
        statuslist = []
        for j in jsondict['statuses']:
            statuslist.append(self.Message(j))
        return statuslist

    def update(self, text):
        '''update a status
        @param text: the update message
        @return: success or not
        '''
        url = "https://api.weibo.com/2/statuses/update.json"
        params = {}
        params['status'] = text
        params['access_token'] = self.token.access_token
        
        ret = self._http_post(url, params)
        try:
            status = self.Message(ret)
            return True
        #TODO:
        #Sometimes update fails, but we do not 
        #catch errors.SNSError. 
        #This part needs further modification. 
#Traceback (most recent call last):
#File "forwarder.py", line 84, in <module>
#% (s.username, s.created_at, s.text)) ):
#File "snsapi/src/app/forwarder/snsapi/plugin/sina.py", line 82, in update
#status = SinaStatus(ret)
#File "snsapi/src/app/forwarder/snsapi/snstype.py", line 21, in __init__
#self.parse(dct)
#File "snsapi/src/app/forwarder/snsapi/plugin/sina.py", line 89, in parse
#self.id = dct["id"]
#KeyError: 'id'
        except:
            return False
        
    def reply(self, statusID, text):
        '''reply to a status
        @param text: the comment text
        @return: success or not
        '''
        url = "https://api.weibo.com/2/comments/create.json"
        params = {}
        params['id'] = statusID.id
        params['comment'] = text
        params['access_token'] = self.token.access_token
        
        ret = self._http_post(url, params)
        try:
            ret['id']
            return True
        except Exception as e:
            logger.info("Reply '%s' to status '%s' fail: %s", text, self.channel_name, ret)
            return False

