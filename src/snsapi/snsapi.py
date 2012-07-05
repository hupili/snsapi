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
import urllib2
import logging
import oauth

class SNSAPI(object):
    def __init__(self):
        self._http_get = oauth._http_get
        self._http_post = oauth._http_post
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
    
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        pass
        
        
        