#-*- encoding: utf-8 -*-

'''
QQ micro-blog client
'''

from ..snsapi import SNSAPI
from ..snstype import Status,User
print "QQ weibo plugged!"

class QQAPI(SNSAPI):
    def __init__(self, channel = None):
        super(QQAPI, self).__init__()
        self.platform = "qq"
        self.domain = "open.t.qq.com"
        self.app_key = ""
        self.app_secret = ""
        self.auth_info.callback_url = "http://copy.the.code.to.client/"
        #you must set self.plaform before invoking read_config()
        if channel:
            self.read_channel(channel)
        else:
            #for backward compatibility
            self.read_config()
            
    def read_channel(self, channel):
        super(QQAPI, self).read_channel(channel) 

        self.channel_name = channel['channel_name']
        self.app_key = channel['app_key']
        self.app_secret = channel['app_secret']

        #We invoke the past config reading method for the moment
        #20120716: after the unifying upgrade of config, 
        #          this is no longer needed
        #self.read_config()
        return 

    def auth(self):
        if self.get_saved_token():
            print "Using a saved access_token!"
            return
        auth_url = "https://open.t.qq.com/cgi-bin/oauth2/"
        #TODO: upgrade mark3
        #      configurable to another call_back url
        #callback_url = "http://copy.the.code.to.client/"
        self.oauth2(auth_url, self.auth_info.callback_url)
        self.save_token()
        
    def attachAuthinfo(self, params):
        params['access_token'] = self.token.access_token
        params['openid'] = self.token.openid
        params['oauth_consumer_key'] = self.app_key
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
                statuslist.append(QQStatus(j))
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
            return True
        return ret
        
class QQStatus(Status):
    def parse(self, dct):
        self.id = dct['id']
        #TODO: unify the data type
        #      In SinaAPI, 'created_at' is a string
        #      In QQAPI, 'created_at' is an int
        #Proposal:
        #      1. Store a copy of dct object in the Status object. 
        #         Derived class of QQAPI or SinaAPI can extract 
        #         other fields for future use. 
        #      2. Defaultly convert every fields into unicode string. 
        #         Upper layer can tackle with a unified interface
        self.created_at = dct['timestamp']
        self.text = dct['text']
        self.reposts_count = dct['count']
        self.comments_count = dct['mcount']
        self.username = dct['name']
        self.usernick = dct['nick']
        
    def show(self):
        print "[%s] at %s \n  %s" % (self.username, self.created_at, self.text)
