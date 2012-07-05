#-*- encoding: utf-8 -*-

'''
SINA micro-blog client
'''

from ..snsapi import SNSAPI
from ..snstype import Status,User
import urllib
import json
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
        params = {}
        params['count'] = count
        params['access_token'] = self.token.access_token
        
        jsonobj = self._http_get(url, params)
        
        statuslist = []
        for j in jsonobj['statuses']:
            statuslist.append(SinaStatus(j))
        return statuslist

        
class SinaStatus(Status):
    def parse(self, dct):
        self.id = dct["id"]
        self.created_at = dct["created_at"]
        self.text = dct['text']
        self.reposts_count = dct['reposts_count']
        self.comments_count = dct['comments_count']
        self.username = dct['user']['name']
        self.usernick = ""
        
    def show(self):
        print "[%s] at %s \n  %s" % (self.username, self.created_at, self.text)