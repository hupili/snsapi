#-*- encoding: utf-8 -*-

'''
SINA micro-blog client
'''

from ..snsapi import SNSAPI
print "SINA weibo plugged!"

class SinaAPI(SNSAPI):
    def __init__(self):
        super(SinaAPI, self).__init__()
        self.app_key = ""
        self.app_secret = ""
        self.domain = "api.sina.com"
        
    def auth(self):
        auth_url = "https://api.weibo.com/oauth2/"
        callback_url = "http://copy.the.code.to.client/"
        self.oauth2(auth_url, callback_url)
        
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        url = "https://api.weibo.com/2/statuses/home_timeline.json"
        count = count
        
        r = self._http_get(url, access_token=self.token.access_token, \
                       count=count)
        