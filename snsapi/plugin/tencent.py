#-*- encoding: utf-8 -*-

'''
QQ micro-blog client
'''

from ..snslog import SNSLog 
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype

logger.debug("%s plugged!", __file__)

class TencentWeiboStatus(SNSBase):

    class Message(snstype.Message):
        def parse(self, dct):
            self.ID.platform = self.platform

            #TODO: unify the data type
            #      In SinaAPI, 'created_at' is a string
            #      In TecentWeibo, 'created_at' is an int
            #Proposal:
            #      1. Store a copy of dct object in the Status object. 
            #         Derived class of TecentWeibo or SinaAPI can extract 
            #         other fields for future use. 
            #      2. Defaultly convert every fields into unicode string. 
            #         Upper layer can tackle with a unified interface
            self.ID.reid = dct['id']
            self.parsed.id = dct['id']
            self.parsed.created_at = dct['timestamp']
            self.parsed.text = dct['text']
            self.parsed.reposts_count = dct['count']
            self.parsed.comments_count = dct['mcount']
            self.parsed.username = dct['name']
            self.parsed.usernick = dct['nick']

    def __init__(self, channel = None):
        super(TencentWeiboStatus, self).__init__(channel)

        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

        #print "bbb"

        #self.app_key = ""
        #self.app_secret = ""
        #if channel:
        #    self.read_channel(channel)
            
    def read_channel(self, channel):
        super(TencentWeiboStatus, self).read_channel(channel) 

        #print "aaaa"

        #self.channel_name = channel['channel_name']
        #self.app_key = channel['app_key']
        #self.app_secret = channel['app_secret']

        if not "auth_url" in self.auth_info:
            self.auth_info.auth_url = "https://open.t.qq.com/cgi-bin/oauth2/"
        if not "callback_url" in self.auth_info:
            self.auth_info.callback_url = "http://copy.the.code.to.client/"

    def auth_first(self):
        self._oauth2_first()

    def auth_second(self):
        self._oauth2_second()
        
    def attachAuthinfo(self, params):
        params['access_token'] = self.token.access_token
        params['openid'] = self.token.openid
        params['oauth_consumer_key'] = self.jsonconf.app_key
        params['oauth_version'] = '2.a'
        params['scope'] = 'all'
        return params

    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        url = "https://open.t.qq.com/api/statuses/home_timeline"
        params = {}
        params['reqnum'] = count
        self.attachAuthinfo(params)
        
        jsonobj = self._http_get(url, params)
        
        statuslist = []
        try:
            for j in jsonobj['data']['info']:
                #statuslist.append(TencentWeiboStatus.Message(j))
                statuslist.append(self.Message(j))
        except TypeError:
            return "Wrong response. " + str(jsonobj)
        return statuslist
    
    def update(self, text):
        '''update a status
        @param text: the update message
        @return: success or not
        '''
        url = "https://open.t.qq.com/api/t/add"
        params = {}
        params["content"] = text
        self.attachAuthinfo(params)
        
        ret = self._http_post(url, params)
        if(ret['msg'] == "ok"):
            #logger.info("Update status '%s' on '%s' succeed", text.decode('utf-8'), self.channel_name)
            logger.info("Update status '%s' on '%s' succeed", text, self.jsonconf.channel_name)
            return True
        return ret
        
    def reply(self, statusID, text):
        '''reply to a status
        @param text: the comment text
        @return: success or not
        '''
        url = "https://open.t.qq.com/api/t/reply"
        params = {}
        params["content"] = text
        params["reid"] = statusID.reid
        self.attachAuthinfo(params)
        
        ret = self._http_post(url, params)
        if(ret['msg'] == "ok"):
            return True
        logger.info("Reply '%s' to status '%s' fail: %s", text, self.jsonconf.channel_name, ret)
        return ret
        
