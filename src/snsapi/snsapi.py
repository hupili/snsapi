# -*- coding: utf-8 -*-

'''
Python client for SNS in China, now supporting Sina and QQ micro-blog
'''
import webbrowser
try:
    import json
except ImportError:
    import simplejson as json
import time
import urllib
import oauth

class SNSAPI(object):
    def __init__(self):
        self.app_key = None
        self.app_secret = None
        self.domain = None
        self.token = None
    
    def oauth2(self, auth_url, callback_url):
        '''Authorizing using synchronized invocation.
        Invoking APIs from oauth.py
        
        web browser will be open, after that, user need to copy the code back to command window.
        save access_token if authorized.
        @param auth_url: the authorizing url for individual SNS provider, must be set.
        @param callback_url: the SNS provider will send something of a code to this page. 
            Users need to collect the code in the browser's address bar to this client.
        '''
        authClient = oauth.APIClient(self.app_key, self.app_secret, callback_url, auth_url=auth_url)
        url = authClient.get_authorize_url()
        webbrowser.open(url)
        
        #Wait for input
        code = raw_input()
        self.token = authClient.request_access_token(code)
        print "Authorized! access token is " + str(self.token)
        
    def _http_get(self, baseurl, params):
        uri = urllib.urlencode(params)
        url = baseurl + "?" + uri
        resp = urllib.urlopen(url)
        json_objs = json.loads(resp.read())
        return json_objs
    
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        pass
        
        
        