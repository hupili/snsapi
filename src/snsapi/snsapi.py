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
from utils import JsonObject
import errors
import base64
import urlparse
import datetime
import snstype
import subprocess

class SNSAPI(object):
    def __init__(self):
        self.app_key = None
        self.app_secret = None
        self.domain = None
        self.token = None
        self.channel_name = None

        self.auth_info = snstype.AuthenticationInfo()

    def fetch_code(self):
        return 

    def request_url(self, url):
        cmd = "%s '%s'" % (self.auth_info.cmd_request_url, url)
        print cmd
        print subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read()
        return

    #build-in fetch_code function: read from console
    def __fetch_code(self):
        print "Please input the whole url from Broswer's address bar:";
        return raw_input()

    #build-in request_url function: open default web browser
    def __request_url(self, url):
        #webbrowser.open(url)
        print url
        return
    
    def oauth2(self, auth_url, callback_url):
        '''Authorizing using synchronized invocation.
        Invoking APIs from oauth.py
        
        web browser will be open, after that, user need to copy the code back to command window.
        save access_token if authorized.
        @param auth_url: the authorizing url for individual SNS provider, must be set.
        @param callback_url: the SNS provider will send something of a code to this page. 
            Users need to collect the code in the browser's address bar to this client.
            callback_url MUST be the same one you set when you apply for an app in openSNS platform.
        '''
        authClient = oauth.APIClient(self.app_key, self.app_secret, callback_url, auth_url=auth_url)
        url = authClient.get_authorize_url()
        #TODO: upgrade mark1
        #      configurable to a cmd to send request
        if self.auth_info.cmd_request_url == "(built-in)" :
            self.__request_url(url)
        else :
            self.request_url(url)
        
        #Wait for input
        #TODO: upgrade mark2
        #      configurable to a cmd to fetch url
        if self.auth_info.cmd_fetch_code == "(built-in)" :
            url = self.__fetch_code()
        else :
            url = self.fetch_code() 
        #url = raw_input()
        self.token = self.parseCode(url)
        self.token.update(authClient.request_access_token(self.token.code))
        print "Authorized! access token is " + str(self.token)
    
    def parseCode(self, url):
        '''
        parse code from url for code and openID
        @param url: contain code and openID
        @return: JsonObject within code and openid
        '''
        return JsonObject(urlparse.parse_qsl(urlparse.urlparse(url).query))

    def save_token(self):
        '''
        access token can be saved, it stays valid for a couple of days
        if successfully saved, invoke get_saved_token() to get it back
        '''
        token = JsonObject(self.token)
        #encrypt access token
        #TODO Use a better encryption method
        token.access_token = base64.encodestring(token.access_token)
        #save token to file "token.save"
        #TODO make the file invisible or at least add it to .gitignore
        fname = self.auth_info.save_token_file
        if fname == "(built-in)" :
            fname = self.channel_name+".token.save"
        if fname != "(null)" :
            with open(fname,"w") as fp:
                json.dump(token, fp)
        
        return True
            
    def get_saved_token(self):
        try:
            fname = self.auth_info.save_token_file
            if fname == "(built-in)" :
                fname = self.channel_name+".token.save"
            if fname != "(null)" :
                with open(fname, "r") as fp:
                    token = JsonObject(json.load(fp))
                    #check expire time
                    if self.isExpired(token):
                        print "Saved Access token is expired, try to get one through sns.auth() :D"
                        return False
                    #decryption
                    token.access_token = base64.decodestring(token.access_token)
                    self.token = token
            else:
                #This channel is configured not to save token to file
                return False
                    
                    #TODO check its expiration time or validity
        except IOError:
            print "No access token saved, try to get one through sns.auth() :D"
            return False
        return True
    
    def isExpired(self, token=None):
        '''
        check if the access token is expired
        '''
        if token == None:
            token = self.token
            
        if token.expires_in < time.time():
            return True
        else:
            return False
    
    def read_channel(self, channel):
        self.channel_name = channel['channel_name']
        if channel['auth_info'] :
            self.auth_info = snstype.AuthenticationInfo(channel['auth_info'])

    #def read_config(self, fname="snsapi/plugin/conf/config.json"):
    #The conf folder is moved to the upper layer(same level as 'test.py'). 
    #It is better handled by application layer, 
    #for the realization information is only available 
    #to application developers and users.
    #def read_config(self, fname="conf/config.json"):
    #    '''get app_key and app_secret
    #    You must set self.platform before invoking this funciton.
    #    This function will change self.app_key and self.app_cecret
    #    @todo: I'm not sure where config.json should be placed, and how to set it in program
    #        without worrying about the execute directory .
    #        and I'm not sure, is it the snsapi layer that should responsible for config file
    #        or upper layer, so I just made a function setup_app()
    #    @param fname: the file path and name of config file, which storing the all app info
    #    @raise NoConfigFile: snsapi/plugin/conf/config.json NOT EXISTS!
    #    @raise NoPlatformInfo: No platform info found in snsapi/plugin/conf/config.json.
    #    @raise MissAPPInfo: Forget app_key and app_secret in snsapi/plugin/conf/config.json
    #    '''
    #    from os.path import abspath
    #    fname = abspath(fname)
    #    try:
    #        with open(fname, "r") as fp:
    #            allinfo = json.load(fp)
    #            for site in allinfo:
    #                
    #                if site['platform'] == self.platform:
    #                    try:
    #                        self.app_key = site['app_key']
    #                        self.app_secret = site['app_secret']
    #                    except KeyError:
    #                        raise errors.MissAPPInfo
    #                    return True
    #            raise errors.NoPlatformInfo
    #    except IOError:
    #        raise errors.NoConfigFile
            
    def setup_app(self, app_key, app_secret):
        '''
        If you do not want to use read_config, and want to set app_key on your own, here it is.
        '''
        self.app_key = app_key
        self.app_secret = app_secret

    def _http_get(self, baseurl, params):
        uri = urllib.urlencode(params)
        url = baseurl + "?" + uri
        resp = urllib.urlopen(url)
        json_objs = json.loads(resp.read())
        return json_objs
    
    def _http_post(self, baseurl, params):
        data = urllib.urlencode(params)
        resp = urllib.urlopen(baseurl,data)
        json_objs = json.loads(resp.read())
        return json_objs
    
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        pass
        
        
        
