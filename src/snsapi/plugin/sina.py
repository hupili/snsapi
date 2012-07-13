#-*- encoding: utf-8 -*-

'''
SINA micro-blog client
'''

from ..snsapi import SNSAPI
from ..snstype import Status,User,Error
from .. import errors
print "SINA weibo plugged!"

class SinaAPI(SNSAPI):
    def __init__(self, channel = None):
        super(SinaAPI, self).__init__()
        
        self.platform = "sina"
        self.domain = "api.sina.com"
        #just you remind myself they exists
        self.app_key = ""
        self.app_secret = ""
        #you must set self.plaform before invoking read_config()
        if channel:
            self.read_channel(channel)
        else:
            #for backward compatibility
            self.read_config()

    def read_channel(self, channel):
        #TODO: fill this stub function

        self.channel_name = channel['channel_name']

        #We invoke the past config reading method for the moment
        self.read_config()
        return 
        
    def auth(self):
        if self.get_saved_token():
            print "Using a saved access_token!"
            return
        auth_url = "https://api.weibo.com/oauth2/"
        callback_url = "http://copy.the.code.to.client/"
        self.oauth2(auth_url, callback_url)
        self.save_token()
        
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
            statuslist.append(SinaStatus(j))
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
            status = SinaStatus(ret)
            return True
        except errors.SNSError:
            return False
        
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
