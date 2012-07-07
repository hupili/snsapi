#-*- encoding: utf-8 -*-

'''
QQ micro-blog client
'''

from ..snsapi import SNSAPI
from ..snstype import Status,User
print "QQ weibo plugged!"

class QQAPI(SNSAPI):
    def __init__(self):
        super(QQAPI, self).__init__()
        self.platform = "qq"
        self.domain = "open.t.qq.com"
        self.app_key = ""
        self.app_secret = ""
        self.read_config()

    def auth(self):
        if self.get_saved_token():
            print "Using a saved access_token!"
            return
        auth_url = "https://open.t.qq.com/cgi-bin/oauth2/"
        callback_url = "http://copy.the.code.to.client/"
        self.oauth2(auth_url, callback_url)
        self.save_token()

    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        url = "https://open.t.qq.com/api/statuses/home_timeline"
        params = {}
        params['reqnum'] = count
        params['access_token'] = self.token.access_token
        params['openid'] = self.token.openid
        params['oauth_consumer_key'] = self.app_key
        params['oauth_version'] = '2.a'
        params['scope'] = 'all'
        
        jsonobj = self._http_get(url, params)
        
        statuslist = []
        for j in jsonobj['data']['info']:
            statuslist.append(QQStatus(j))
        return statuslist
    
class QQStatus(Status):
    def parse(self, dct):
        self.id = dct["id"]
        self.created_at = dct["timestamp"]
        self.text = dct['text']
        self.reposts_count = dct['count']
        self.comments_count = dct['mcount']
        self.username = dct['name']
        self.usernick = dct['nick']
        
    def show(self):
        print "[%s] at %s \n  %s" % (self.username, self.created_at, self.text)