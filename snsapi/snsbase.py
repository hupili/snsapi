# -*- coding: utf-8 -*-

'''
snsapi base class. 

All plugins are derived from this class. 
It provides common authenticate and communicate methods.
'''

# === system imports ===
import webbrowser
from utils import json
import urllib
import urllib2
from errors import snserror
import base64
import urlparse
import datetime
import subprocess
import functools

# === snsapi modules ===
import snstype
import utils
from snslog import SNSLog as logger

# === 3rd party modules ===
from third import oauth
oauth.logger = logger

def require_authed(func):
    '''
    A decorator to require auth before an operation

    '''
    @functools.wraps(func)
    def wrapper_require_authed(self, *al, **ad):
        if self.is_authed():
            return func(self, *al, **ad)
        else:
            logger.warning("Channel '%s' is not authed!", self.jsonconf['channel_name'])
            return 
    doc_orig = func.__doc__ if func.__doc__ else ''
    doc_new = doc_orig + '\n        **NOTE: This method require authorization before invokation.**'
    wrapper_require_authed.__doc__ = doc_new
    return wrapper_require_authed


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
        self.console_output = lambda : utils.console_output()
        #self.utc2str = lambda u: utils.utc2str(u)
        #self.str2utc = lambda s: utils.str2utc(s)
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
        elif self.auth_info.cmd_fetch_code == "(authproxy_username_password)":
            # Currently available for SinaWeibo. 
            # Before using this method, please deploy one authproxy:
            #    * https://github.com/xuanqinanhai/weibo-simulator/
            # Or, you can use the official one:
            #    * https://snsapi.ie.cuhk.edu.hk/authproxy/auth.php
            # (Not recommended; only for test purpose; do not use in production)
            try:
                login_username = self.auth_info.login_username
                login_password = self.auth_info.login_password
                app_key = self.jsonconf.app_key
                app_secret = self.jsonconf.app_secret
                callback_url = self.auth_info.callback_url
                authproxy_url = self.auth_info.authproxy_url
                params = urllib.urlencode({'userid': login_username,
                    'password': login_password, 'app_key': app_key,
                    'app_secret': app_secret,'callback_uri': callback_url})
                req = urllib2.Request(url=authproxy_url, data=params);
                code = urllib2.urlopen(req).read()
                logger.debug("response from authproxy: %s", code)
                # Just to conform to previous SNSAPI convention
                return "http://snsapi.snsapi/?code=%s" % code
            except Exception, e:
                logger.warning("Catch exception: %s", e)
                raise snserror.auth.fetchcode
        elif self.auth_info.cmd_fetch_code == "(local_username_password)":
            # Currently available for SinaWeibo. 
            # The platform must implement _fetch_code_local_username_password() method
            try:
                return self._fetch_code_local_username_password()
            except Exception, e:
                logger.warning("Catch exception: %s", e)
                raise snserror.auth.fetchcode
        else:  # Execute arbitrary command to fetch code
            cmd = "%s %s" % (self.auth_info.cmd_fetch_code, self.__last_request_time)
            logger.debug("fetch_code command is: %s", cmd) 
            ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.readline().rstrip()
            tries = 1 
            while str(ret) == "null" :
                tries += 1
                if tries > self.__fetch_code_max_try :
                    break
                time.sleep(self.__fetch_code_timeout)
                ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().rstrip()
            return ret

    def request_url(self, url):
        self._last_requested_url = url
        if self.auth_info.cmd_request_url == "(webbrowser)" :
            self.open_brower(url)
        elif self.auth_info.cmd_request_url == "(dummy)" :
            logger.debug("dummy method used for request_url(). Do nothing.")
            pass
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
        else:  # Execute arbitrary command to request url
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
        try:
            self.__init_oauth2_client() 
            url = self.fetch_code() 
            logger.debug("get url: %s", url)
            if str(url) == "null" :
                raise snserror.auth
            self.token = self._parse_code(url)
            self.token.update(self.auth_client.request_access_token(self.token.code))
            logger.debug("Authorized! access token is " + str(self.token))
            logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None
    
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

    def auth_first(self):
        self._oauth2_first()

    def auth_second(self):
        try:
            self._oauth2_second()
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None

    def open_brower(self, url):
        return webbrowser.open(url)
    
    def _parse_code(self, url):
        '''
        Parse code from a URL containing ``code=xx`` parameter

        :param url: 
            contain code and optionally other parameters

        :return: JsonDict containing 'code' and (optional) other URL parameters

        '''
        return utils.JsonDict(urlparse.parse_qsl(urlparse.urlparse(url).query))

    def save_token(self):
        '''
        access token can be saved, it stays valid for a couple of days
        if successfully saved, invoke get_saved_token() to get it back
        '''
        fname = self.auth_info.save_token_file
        if fname == "(default)" :
            fname = self.jsonconf.channel_name+".token.save"
        # Do not save expired token (or None type token)
        if not fname is None and not self.is_expired():
            #TODO: encrypt access token
            token = utils.JsonObject(self.token)
            with open(fname,"w") as fp:
                json.dump(token, fp)
        
        return True
            
    def get_saved_token(self):
        try:
            fname = self.auth_info.save_token_file
            if fname == "(default)" :
                fname = self.jsonconf.channel_name+".token.save"
            if not fname is None:
                with open(fname, "r") as fp:
                    token = utils.JsonObject(json.load(fp))
                    # check expire time
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

    def expire_after(self, token = None):
        '''
        Calculate how long it is before token expire. 

        :return:

           * >0: the time in seconds. 
           * 0: has already expired. 
           * -1: there is no token expire issue for this platform. 

        '''
        if token == None:
            token = self.token
        if token:
            if token.expires_in - self.time() > 0: 
                return token.expires_in - self.time()
            else: 
                return 0 
        else: 
            # If there is no 'token' attribute available, 
            # we regard it as token expired. 
            return 0

    def is_expired(self, token = None):
        '''
        Check if the access token is expired. 

        It delegates the logic to 'expire_after', which is a more 
        formal module to use. This interface is kept for backward
        compatibility. 
        '''
        #TODO:
        #    For those token that are near 0, we'd better inform
        #    the upper layer somehow. Or, it may just expire when 
        #    the upper layer calls. 
        if self.expire_after(token) == 0:
            return True
        else:
            # >0 (not expire) or ==-1 (no expire issue)
            return False

    def is_authed(self):
        return False if self.is_expired() else True

    def need_auth(self):
        '''
        Whether this platform requires two-stage authorization.

        Note:

           * Some platforms have authorization flow but we do not use it,
             e.g. Twitter, where we have a permanent key for developer
             They'll return False.
           * If your platform do need authorization, please override this
             method in your subclass.

        '''

        return False

    @staticmethod
    def new_channel(full = False):
        '''
        Return a JsonDict object containing channel configurations. 

        :param full: Whether to return all config fields.

           * False: only returns essential fields. 
           * True: returns all fields (essential + optional). 

        '''

        c = utils.JsonDict()
        c['channel_name'] = 'new_channel_name'
        c['open'] = 'yes'

        if full:
            c['description'] = "a string for you to memorize"
            # Defaultly enabled methods in SNSPocket batch operation
            c['methods'] = "" 

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

        #if not 'text_length_limit' in self.jsonconf:
        #    self.jsonconf['text_length_limit'] = 140

    def setup_oauth_key(self, app_key, app_secret):
        '''
        If you do not want to use read_channel, and want to set app_key on your own, here it is.
        '''
        self.jsonconf.app_key = app_key
        self.jsonconf.app_secret = app_secret

    def _http_get(self, baseurl, params):
        '''Use HTTP GET to request a JSON interface

        :param baseurl: Base URL before parameters

        :param params: a dict of params (can be unicode)

        :return: 
        
           * Success: A JSON compatible structure
           * Failure: A {}. Warning is logged. 
        '''
        # Support unicode parameters. 
        # We should encode them as exchanging stream (e.g. utf-8)
        # before URL encoding and issue HTTP requests. 
        try:
            for p in params:
                params[p] = self._unicode_encode(params[p])
            uri = urllib.urlencode(params)
            url = baseurl + "?" + uri
            resp = urllib.urlopen(url)
            json_objs = json.loads(resp.read())
            return json_objs
        except Exception, e:
            # Tolerate communication fault, like network failure. 
            logger.warning("_http_get fail: %s", e)
            return {}
    
    def _http_post(self, baseurl, params):
        '''Use HTTP POST to request a JSON interface. 

        See ``_http_get`` for more info.
        '''
        try:
            for p in params:
                params[p] = self._unicode_encode(params[p])
            data = urllib.urlencode(params)
            resp = urllib.urlopen(baseurl,data)
            json_objs = json.loads(resp.read())
            return json_objs
        except Exception, e:
            logger.warning("_http_post fail: %s", e)
            return {}

    def _unicode_encode(self, s):
        """
        Detect if a string is unicode and encode as utf-8 if necessary
        """
        if isinstance(s, unicode):
            return s.encode('utf-8') 
        else:
            return s
    
    def _expand_url(self, url):
        '''
        expand a shorten url
        
        :param url:
            The url will be expanded if it is a short url, or it will
            return the origin url string. url should contain the protocol
            like "http://"
        '''
        try:
            ex_url = urllib.urlopen(url)
            if ex_url.url == url:
                return ex_url.url
            else:
                return self._expand_url(ex_url.url)
        except IOError, e:
            # Deal with "service or name unknow" error
            logger.warning('Error when expanding URL. Maybe invalid URL: %s', e)
            return url

    def _cat(self, length, text_list, delim = "||"):
        '''
        Concatenate strings. 

        :param length:
            The output should not exceed length unicode characters. 

        :param text_list:
            A list of text pieces. Each element is a tuple (text, priority). 
            The _cat function will concatenate the texts using the order in 
            text_list. If the output exceeds length, (part of) some texts 
            will be cut according to the priority. The lower priority one 
            tuple is assigned, the earlier it will be cut. 

        '''
        if length:
            order_list = zip(range(0, len(text_list)), text_list)
            order_list.sort(key = lambda tup: tup[1][1])
            extra_length = sum([len(t[1][0]) for t in order_list]) \
                    - length + len(delim) * (len(order_list) - 1)

            output_list = []
            for (o, (t, p)) in order_list:
                if extra_length <= 0:
                    output_list.append((o, t, p))
                elif extra_length >= len(t):
                    extra_length -= len(t)
                else:
                    output_list.append((o, t[0:(len(t) - extra_length)], p))
                    extra_length = 0 

            output_list.sort(key = lambda tup: tup[0])
            return delim.join([t for (o, t, p) in output_list])
        else:
            # length is None, meaning unlimited
            return delim.join([t for (t, p) in text_list])


    # Just a memo of possible methods

    # def home_timeline(self, count=20):
    #     '''Get home timeline
    #     get statuses of yours and your friends'
    #     @param count: number of statuses
    #     Always returns a list of Message objects. If errors happen in the 
    #     requesting process, return an empty list. The plugin is recommended
    #     to log warning message for debug use. 
    #     '''
    #     pass
         
    # def update(self, text):
    #     """docstring for update"""
    #     pass

    # def reply(self, mID, text):
    #     """docstring for reply"""
    #     pass

    @require_authed
    def forward(self, message, text):
        """
        A general forwarding implementation using update method. 
        
        :param message:
            The Message object. The message you want to forward. 

        :param text:
            A unicode string. The comments you add to the message. 

        :return:
            Successful or not: True / False 

        """
        
        if not isinstance(message, snstype.Message):
            logger.warning("unknown type to forward: %s", type(message))
            return False

        if self.update == None:
            # This warning message is for those who build application on 
            # individual plugin classes. If the developers based their app
            # on SNSPocket, they will see the warning message given by the 
            # dummy update method. 
            logger.warning("this platform does not have update(). can not forward")
            return False

        tll = None
        if 'text_length_limit' in self.jsonconf:
            tll = self.jsonconf['text_length_limit']
        #orig_text = "[%s:%s][%s]%s" % (message.platform, message.parsed.username, \
        #        utils.utc2str(message.parsed.time), message.parsed.text)
        #if 'platform_prefix' in self.jsonconf:
        #    platform_prefix = self.jsonconf['platform_prefix']
        #else:

        #TODO:
        #    This mapping had better be configurable from user side
        mapping = {
                'RSS': u'RSS',
                'RSS2RW': u'RSS2RW',
                'RenrenShare': u'人人',
                'RenrenStatus': u'人人',
                'SQLite': u'SQLite',
                'SinaWeiboStatus': u'新浪',
                'TencentWeiboStatus': u'腾讯',
                'TwitterStatus': u'推特',
                'Email': u'伊妹'
        }

        platform_prefix = message.platform
        if platform_prefix in mapping:
            platform_prefix = mapping[platform_prefix]
        last_user = "[%s:%s]" % (platform_prefix, message.parsed.username)
        if 'text_orig' in message.parsed and 'text_trace' in message.parsed:
            #TODO:
            #
            # We wrap unicode() here, in case the 'text_trace' field
            # or 'text_orig' field is parsed to None. 
            #
            # This problem can also be solved at _cat() function. In 
            # this way, it we can compat the message further. i.e. 
            # When one field is None, we omit the text "None" and 
            # delimiter.
            final = self._cat(tll, [(text, 5), (last_user, 4), \
                    (unicode(message.parsed.text_trace), 1), \
                    (unicode(message.parsed.text_orig), 3)])
        else:
            final = self._cat(tll, [(text, 3), (last_user, 2),\
                    (unicode(message.parsed.text), 1)])
       
        #print final
        return self.update(final)
