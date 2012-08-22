#-*- encoding: utf-8 -*-

'''
renren client
'''
print "renren plugged!"

import urllib
import webbrowser
import time
import hashlib

try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)

_entry_class_ = "RenrenAPI"

g_scope = "read_user_status"
g_redirect_uri = "http://graph.renren.com/oauth/login_success.html"

#global RENREN_APP_API_KEY
#global RENREN_APP_SECRET_KEY
RENREN_APP_API_KEY = ""
RENREN_APP_SECRET_KEY = ""

RENREN_AUTHORIZATION_URI = "http://graph.renren.com/oauth/authorize"
RENREN_ACCESS_TOKEN_URI = "http://graph.renren.com/oauth/token"
RENREN_SESSION_KEY_URI = "http://graph.renren.com/renren_api/session_key"
RENREN_API_SERVER = "http://api.renren.com/restserver.do"

def request():
    args = dict(client_id=RENREN_APP_API_KEY, redirect_uri = g_redirect_uri)
    args["response_type"] = "code"
    args["scope"] = g_scope
    args["state"] = "1 23 abc&?|."
    url = RENREN_AUTHORIZATION_URI + "?" + urllib.urlencode(args)
    print url
    webbrowser.open(url)

def auth(code = None):
    if code is None :
        code = raw_input()
    args = dict(client_id=RENREN_APP_API_KEY, redirect_uri=g_redirect_uri)
    scope = g_scope
    scope_array = str(scope).split("[\\s,+]")
    args["client_secret"] = RENREN_APP_SECRET_KEY
    args["code"] = code
    args["grant_type"] = "authorization_code"
    response = urllib.urlopen(RENREN_ACCESS_TOKEN_URI + "?" + urllib.urlencode(args)).read()
    print response
    access_token = _parse_json(response)["access_token"]
    return access_token

class RenRenAPIClient(object):
    def __init__(self, session_key = None, api_key = None, secret_key = None):
        self.session_key = session_key
        self.api_key = api_key
        self.secret_key = secret_key
    def request(self, params = None):
        """Fetches the given method's response returning from RenRen API.

        Send a POST request to the given method with the given params.
        """
        params["api_key"] = self.api_key
        params["call_id"] = str(int(time.time() * 1000))
        params["format"] = "json"
        params["session_key"] = self.session_key
        params["v"] = '1.0'
        sig = self.hash_params(params);
        params["sig"] = sig
        
        post_data = None if params is None else urllib.urlencode(params)
        
        file = urllib.urlopen(RENREN_API_SERVER, post_data)
        
        try:
            s = file.read()
            #logging.info("api response is: " + s)
            response = _parse_json(s)
        finally:
            file.close()

        print "api response is: %s" % response

        if type(response) is not list and "error_code" in response:
            print response["error_msg"]
            raise RenRenAPIError(response["error_code"], response["error_msg"])
        return response

    def hash_params(self, params = None):
        hasher = hashlib.md5("".join(["%s=%s" % (self.unicode_encode(x), self.unicode_encode(params[x])) for x in sorted(params.keys())]))
        hasher.update(self.secret_key)
        return hasher.hexdigest()
    def unicode_encode(self, str):
        """
        Detect if a string is unicode and encode as utf-8 if necessary
        """
        return isinstance(str, unicode) and str.encode('utf-8') or str
    
class RenRenAPIError(Exception):
    def __init__(self, code, message):
        Exception.__init__(self, message)
        self.code = code

def read_status(atoken):
    session_key_request_args = {"oauth_token": atoken}
    response = urllib.urlopen(RENREN_SESSION_KEY_URI + "?" + urllib.urlencode(session_key_request_args)).read()
    session_key = str(_parse_json(response)["renren_token"]["session_key"])
    api_params = dict(method = "status.gets", page = 1, count = 20)
    api_client = RenRenAPIClient(session_key, RENREN_APP_API_KEY, RENREN_APP_SECRET_KEY)
    response = api_client.request(api_params)
    print response

def read_conf():
    global RENREN_APP_API_KEY
    global RENREN_APP_SECRET_KEY
    conf = json.load(open('../../conf/channel.json'))
    for c in conf:
        if c['platform'] == 'renren':
            RENREN_APP_API_KEY = c['app_key']
            RENREN_APP_SECRET_KEY = c['app_secret']

if __name__ == "__main__":
    read_conf()
    request()
    atoken = auth()
    print atoken
    read_status(atoken)
