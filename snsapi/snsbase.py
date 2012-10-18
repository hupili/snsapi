# -*- coding: utf-8 -*-

'''
snsapi base class. 

All plugins are derived from this class. 
It provides common authenticate and communicate methods.
'''

# === system imports ===
import webbrowser
try:
    import json
except ImportError:
    import simplejson as json
import urllib
from errors import snserror
import base64
import urlparse
import datetime
import subprocess

# === snsapi modules ===
import snstype
import utils
#from utils import JsonObject
from snslog import SNSLog
logger = SNSLog

# === 3rd party modules ===
from third import oauth

class SNSBase(object):
    def __init__(self, channel = None):

        self.token = None

        self.auth_info = snstype.AuthenticationInfo()
        self.__fetch_code_timeout = 2
        self.__fetch_code_max_try = 30

        # methods binding
        import time
        self.time = lambda : time.time()
        self.console_input = lambda : utils.console_input()
        self._urlencode = lambda params : urllib.urlencode(params)
        
        # We can not init the auth client here. 
        # As the base class, this part is first 
        # executed. Not until we execute the derived
        # class, e.g. sina.py, can we get all the
        # information to init an auth client. 
        self.auth_client = None

        if channel:
            self.read_channel(channel)

    def fetch_code(self):
        if self.auth_info.cmd_fetch_code == "(console_input)" :
            utils.console_output("Please input the whole url from Broswer's address bar:")
            return self.console_input().strip()
        elif self.auth_info.cmd_fetch_code == "(local_webserver)":
            try: 
                self.httpd.handle_request()
                if 'code' in self.httpd.query_params:
                    code = self.httpd.query_params['code']
                    logger.info("Get code from local server: %s", code)
                    return "http://localhost/?%s" % urllib.urlencode(self.httpd.query_params)
                else:
                    #TODO:
                    #    There is a non repeatable bug here. 
                    #    When we have multiple platforms to authorize, 
                    #    successive platforms may fail in this branch. 
                    #    That means there is other HTTP request to the local HTTP server
                    #    before the call_back URL. 
                    #
                    #    Solution:
                    #        * Configure different port for different channels. 
                    #          This is solved at upper layer. 
                    #        * Support random port by default. 
                    raise snserror.auth.fetchcode
            finally:
                del self.httpd
        else :
            cmd = "%s %s" % (self.auth_info.cmd_fetch_code, self.__last_request_time)
            logger.debug("fetch_code command is: %s", cmd) 
            ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.readline().rstrip()
            tries = 1 
            while ret == "(null)" :
                tries += 1
                if tries > self.__fetch_code_max_try :
                    break
                time.sleep(self.__fetch_code_timeout)
                ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().rstrip()
            return ret

    def request_url(self, url):
        if self.auth_info.cmd_request_url == "(webbrowser)" :
            self.open_brower(url)
        elif self.auth_info.cmd_request_url == "(console_output)" :
            utils.console_output(url)
        elif self.auth_info.cmd_request_url == "(local_webserver)+(webbrowser)" :
            host = self.auth_info.host 
            port = self.auth_info.port 
            from third.server import ClientRedirectServer
            from third.server import ClientRedirectHandler
            import socket
            try:
                self.httpd = ClientRedirectServer((host, port), ClientRedirectHandler)
                self.open_brower(url)
            except socket.error:
                raise snserror.auth
        else :
            self.__last_request_time = self.time()
            cmd = "%s '%s'" % (self.auth_info.cmd_request_url, url)
            logger.debug("request_url command is: %s", cmd) 
            res = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().rstrip()
            logger.debug("request_url result is: %s", res) 
            return

    # The init process is separated out and we 
    # adopt an idle evaluation strategy for it. 
    # This is because the two stages of OAtuh 
    # should be context-free. We can not assume 
    # calling the second is right after calling
    # the first. They can be done in different 
    # invokation of the script. They can be done
    # on different servers. 
    def __init_oauth2_client(self):
        if self.auth_client == None:
            try:
                self.auth_client = oauth.APIClient(self.jsonconf.app_key, \
                        self.jsonconf.app_secret, self.auth_info.callback_url, \
                        auth_url = self.auth_info.auth_url)
            except:
                logger.critical("auth_client init error")
                raise snserror.auth

    def _oauth2_first(self):
        '''
        The first stage of oauth. 
        Generate auth url and request. 
        '''
        self.__init_oauth2_client()

        url = self.auth_client.get_authorize_url()

        self.request_url(url)

    def _oauth2_second(self):
        '''
        The second stage of oauth. 
        Fetch authenticated code. 
        '''
        self.__init_oauth2_client() 

        url = self.fetch_code() 
        if url == "(null)" :
            raise snserror.auth
        self.token = self.parseCode(url)
        self.token.update(self.auth_client.request_access_token(self.token.code))
        logger.debug("Authorized! access token is " + str(self.token))
        logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)
    
    def oauth2(self):
        '''
        Authorizing using synchronized invocation of OAuth2.


        Users need to collect the code in the browser's address bar to this client.
        callback_url MUST be the same one you set when you apply for an app in openSNS platform.
        '''
        
        logger.info("Try to authenticate '%s' using OAuth2", self.jsonconf.channel_name)
        self._oauth2_first()
        self._oauth2_second()

    def auth(self):
        """
        General entry for authorization.  
        It uses OAuth2 by default. 
        """
        if self.get_saved_token():
            return
        self.oauth2()
        self.save_token()
    
    def open_brower(self, url):
        return webbrowser.open(url)
    
    def parseCode(self, url):
        '''
        .. py:function:: -

        :param url: 
            contain code and openID

        :return: JsonObject within code and openid
        '''
        return utils.JsonObject(urlparse.parse_qsl(urlparse.urlparse(url).query))

    def save_token(self):
        '''
        access token can be saved, it stays valid for a couple of days
        if successfully saved, invoke get_saved_token() to get it back
        '''
        token = utils.JsonObject(self.token)
        #TODO: encrypt access token

        fname = self.auth_info.save_token_file
        if fname == "(default)" :
            fname = self.jsonconf.channel_name+".token.save"
        if fname != "(null)" :
            with open(fname,"w") as fp:
                json.dump(token, fp)
        
        return True
            
    def get_saved_token(self):
        try:
            fname = self.auth_info.save_token_file
            if fname == "(default)" :
                fname = self.jsonconf.channel_name+".token.save"
            if fname != "(null)" :
                with open(fname, "r") as fp:
                    token = utils.JsonObject(json.load(fp))
                    #check expire time
                    if self.is_expired(token):
                        logger.debug("Saved Access token is expired, try to get one through sns.auth() :D")
                        return False
                    #TODO: decrypt token
                    self.token = token
            else:
                logger.debug("This channel is configured not to save token to file")
                return False
                    
        except IOError:
            logger.debug("No access token saved, try to get one through sns.auth() :D")
            return False

        logger.info("Read saved token for '%s' successfully", self.jsonconf.channel_name)
        return True
    
    def is_expired(self, token=None):
        '''
        check if the access token is expired
        '''
        if token == None:
            token = self.token
            
        if token.expires_in < self.time():
            return True
        else:
            return False

    @staticmethod
    def new_channel(full = False):
        '''
        Return a JsonDict object containing channel configurations. 

        full:
            False: only returns essential fields. 
            True: returns all fields (essential + optional). 

        '''

        c = utils.JsonDict()
        c['channel_name'] = 'new_channel_name'
        c['open'] = 'yes'

        if full:
            c['description'] = "a string for you to memorize"

        return c
    
    def read_channel(self, channel):
        self.jsonconf = utils.JsonDict(channel)

        if 'auth_info' in channel :
            self.auth_info.update(channel['auth_info'])
            self.auth_info.set_defaults()

        if not 'host' in self.auth_info:
            self.auth_info['host'] = 'localhost'
        if not 'port' in self.auth_info:
            self.auth_info['port'] = 12121

    def setup_oauth_key(self, app_key, app_secret):
        '''
        If you do not want to use read_channel, and want to set app_key on your own, here it is.
        '''
        self.jsonconf.app_key = app_key
        self.jsonconf.app_secret = app_secret

    def _http_get(self, baseurl, params):
        # Support unicode parameters. 
        # We should encode them as exchanging stream (e.g. utf-8)
        # before URL encoding and issue HTTP requests. 
        for p in params:
            params[p] = self._unicode_encode(params[p])
        uri = urllib.urlencode(params)
        url = baseurl + "?" + uri
        resp = urllib.urlopen(url)
        json_objs = json.loads(resp.read())
        return json_objs
    
    def _http_post(self, baseurl, params):
        for p in params:
            params[p] = self._unicode_encode(params[p])
        data = urllib.urlencode(params)
        resp = urllib.urlopen(baseurl,data)
        json_objs = json.loads(resp.read())
        return json_objs

    def _unicode_encode(self, s):
        """
        Detect if a string is unicode and encode as utf-8 if necessary
        """
        if isinstance(s, unicode):
            return s.encode('utf-8') 
        else:
            return s
    
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses

        Always returns a list of Message objects. If errors happen in the 
        requesting process, return an empty list. The plugin is recommended
        to log warning message for debug use. 
        '''
        pass
        
