#-*- encoding: utf-8 -*-

'''
SINA micro-blog client
'''

from ..snslog import SNSLog 
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype
from ..errors import snserror

logger.debug("%s plugged!", __file__)

class SinaWeiboStatus(SNSBase):

    class Message(snstype.Message):
        def parse(self):
            self.ID.platform = self.platform
            self._parse(self.raw)

        def _parse(self, dct):
            #print dct 

            self.ID.id = dct["id"]

            self.parsed.time = dct["created_at"]
            self.parsed.username = dct['user']['name']
            self.parsed.userid = dct['user']['id']

            self.parsed.reposts_count = dct['reposts_count']
            self.parsed.comments_count = dct['comments_count']
            
            if 'retweeted_status' in dct:
                self.parsed.username_orig = dct['retweeted_status']['user']['name']
                self.parsed.text_orig = dct['retweeted_status']['text']
                self.parsed.text_trace = dct['text']
                self.parsed.text = self.parsed.text_trace \
                        + " || " + "@" + self.parsed.username_orig \
                        + " : " + self.parsed.text_orig
            else:
                self.parsed.text_orig = dct['text'] 
                self.parsed.text_trace = None
                self.parsed.text = self.parsed.text_orig

            #TODO: clean past fields
            #self.parsed.id = dct["id"]
            #self.parsed.created_at = dct["created_at"]
            #self.parsed.text = dct['text']
            #self.parsed.reposts_count = dct['reposts_count']
            #self.parsed.comments_count = dct['comments_count']
            #self.parsed.username = dct['user']['name']
            #self.parsed.usernick = ""

    def __init__(self, channel = None):
        super(SinaWeiboStatus, self).__init__(channel)
        
        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['app_key'] = ''
        c['app_secret'] = ''
        c['platform'] = 'SinaWeiboStatus'
        c['auth_info'] = {
                "save_token_file": "(default)", 
                "cmd_request_url": "(default)", 
                "callback_url": "https://snsapi.ie.cuhk.edu.hk/aux/auth.php", 
                "cmd_fetch_code": "(default)" 
                } 

        return c

    def read_channel(self, channel):
        super(SinaWeiboStatus, self).read_channel(channel) 

        if not "auth_url" in self.auth_info:
            self.auth_info.auth_url = "https://api.weibo.com/oauth2/"
        if not "callback_url" in self.auth_info:
            self.auth_info.callback_url = "http://copy.the.code.to.client/"

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
            logger.info("Update status '%s' on '%s' succeed", text, self.jsonconf.channel_name)
            return True
        except Exception, e:
            logger.warning("Update status fail. Message: %s", e.message)
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
            logger.info("Reply '%s' to status '%s' fail: %s", text, self.jsonconf.channel_name, ret)
            return False

