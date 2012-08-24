#-*- encoding: utf-8 -*-

'''
renren client
'''

from ..snslog import SNSLog
logger = SNSLog
from ..snsapi import oauth
from ..snsapi import SNSAPI
from ..snstype import Status,User,Error
from .. import errors
#Use by all Renren API transactions
import urllib
#Used by renren_request
import time
#Used by __hash_params
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
logger.debug("%s plugged!", _entry_class_)

# Inteface URLs.
# This differs from other platforms
RENREN_AUTHORIZATION_URI = "http://graph.renren.com/oauth/authorize"
RENREN_ACCESS_TOKEN_URI = "http://graph.renren.com/oauth/token"
RENREN_SESSION_KEY_URI = "http://graph.renren.com/renren_api/session_key"
RENREN_API_SERVER = "http://api.renren.com/restserver.do"


class RenrenAPI(SNSAPI):
    def __init__(self, channel = None):
        super(RenrenAPI, self).__init__()
        
        self.platform = "renren"
        self.domain = "graph.renren.com"
        self.app_key = ""
        self.app_secret = ""
        self.auth_info.callback_url = "http://graph.renren.com/oauth/login_success.html"
        if channel:
            self.read_channel(channel)

    def read_channel(self, channel):
        super(RenrenAPI, self).read_channel(channel) 

        self.channel_name = channel['channel_name']
        self.app_key = channel['app_key']
        self.app_secret = channel['app_secret']
        
    def auth_first(self):
        args = dict(client_id=self.app_key, redirect_uri = self.auth_info.callback_url)
        args["response_type"] = "code"
        args["scope"] = "read_user_status status_update publish_comment"
        args["state"] = "snsapi! Stand up, Geeks! Step on the head of those evil platforms!"
        url = RENREN_AUTHORIZATION_URI + "?" + urllib.urlencode(args)
        self.request_url(url)

    def auth_second(self):
        #TODO:
        #    The name 'fetch_code' is not self-explained.
        #    It actually fetches the authenticated callback_url.
        #    Code is parsed from this url. 
        url = self.fetch_code()
        self.token = self.parseCode(url)
        args = dict(client_id=self.app_key, redirect_uri = self.auth_info.callback_url)
        args["client_secret"] = self.app_secret
        args["code"] = self.token.code
        args["grant_type"] = "authorization_code"
        response = urllib.urlopen(RENREN_ACCESS_TOKEN_URI + "?" + urllib.urlencode(args)).read()
        #print response
        self.token.update(_parse_json(response))
        self.token.expires_in = self.token.expires_in + time.time()

    def auth(self):
        if self.get_saved_token():
            print "Using a saved access_token!"
            return
        self.auth_first()
        self.auth_second()
        self.save_token()
        print "Authorized! access token is " + str(self.token)

    def renren_request(self, params = None):
        """
        A general purpose encapsulation of renren API. 
        It fills in system paramters and compute the signature. 
        """

        #request a session key
        session_key_request_args = {"oauth_token": self.token.access_token}
        response = urllib.urlopen(RENREN_SESSION_KEY_URI + "?" + urllib.urlencode(session_key_request_args)).read()
        session_key = str(_parse_json(response)["renren_token"]["session_key"])

        #system parameters fill-in
        params["api_key"] = self.app_key
        params["call_id"] = str(int(time.time() * 1000))
        params["format"] = "json"
        params["session_key"] = session_key
        params["v"] = '1.0'
        #del 'sig' first, if not:
        #   Client may use the same params dict repeatedly. 
        #   Later call will fail because they have previous 'sig'. 
        if "sig" in params:
            del params["sig"] 
        sig = self.__hash_params(params);
        params["sig"] = sig
        
        post_data = None if params is None else urllib.urlencode(params)
        
        file = urllib.urlopen(RENREN_API_SERVER, post_data)
        
        try:
            s = file.read()
            response = _parse_json(s)
        finally:
            file.close()

        if type(response) is not list and "error_code" in response:
            #TODO: using logging
            print response["error_msg"]
            raise errors.RenRenAPIError(response["error_code"], response["error_msg"])
        return response

    def __hash_params(self, params = None):
        hashstring = "".join(["%s=%s" % (self.__unicode_encode(x), self.__unicode_encode(params[x])) for x in sorted(params.keys())])
        #print hashstring
        hashstring = hashstring + self.__unicode_encode(self.app_secret)
        #print "=== _hash_params"
        #print hashstring
        #print "=== _hash_params"
        hasher = hashlib.md5(hashstring)
        return hasher.hexdigest()

    def __unicode_encode(self, str):
        """
        Detect if a string is unicode and encode as utf-8 if necessary
        """
        return isinstance(str, unicode) and str.encode('utf-8') or str
        
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''

        #api_params = dict(method = "status.gets", page = 1, count = 20)
        api_params = dict(method = "feed.get", type = 10, page = 1, count = count)
        jsonlist = self.renren_request(api_params)
        
        statuslist = []
        for j in jsonlist:
            statuslist.append(RenrenStatus(j))
        return statuslist

    def update(self, text):
        '''update a status
        @param text: the update message
        @return: success or not
        '''

        api_params = dict(method = "status.set", status = text)
        
        try:
            ret = self.renren_request(api_params)
            #print ret
            if 'result' in ret and ret['result'] == 1:
                return True
            else:
                return False
        except:
            return False

    def reply(self, statusID, text):
        """reply status
        @param status: StatusID object
        @param text: string, the reply message
        @return: success or not
        """

        #TODO: check platform and place a warning
        #      if it is not "renren"

        api_params = dict(method = "status.addComment", content = text, \
            status_id = statusID.status_id, owner_id = statusID.source_user_id)

        try:
            ret = self.renren_request(api_params)
            if 'result' in ret and ret['result'] == 1:
                return True
            else:
                return False
        except:
            return False

        
#TODO: 
#    "Status" is not an abstract enough word. 
#    Suggested to change it to "Message". 
#    There are many types of messages on renren. 
#    There are even many types for new feeds alone. 
#    Ref: http://wiki.dev.renren.com/wiki/Type%E5%88%97%E8%A1%A8
class RenrenStatus(Status):
    def parse(self, dct):
        self.ID.platform = "renren"
        self._parse_feed_status(dct)

    def _parse_feed_status(self, dct):
        #print json.dumps(dct)
        #By trial, it seems:
        #   * 'post_id' : the id of news feeds
        #   * 'source_id' : the id of status
        #     equal to 'status_id' returned by 
        #     'status.get' interface
        #self.id = dct["post_id"]
        self.id = dct["source_id"]
        self.created_at = dct["update_time"]
        self.text = dct['message']
        self.reposts_count = 'N/A'
        self.comments_count = dct['comments']['count']
        self.username = dct['name']
        self.usernick = ""
        self.ID.status_id = dct["source_id"]
        self.ID.source_user_id = dct["actor_id"]

    def _parse_status(self, dct):
        self.id = dct["status_id"]
        self.created_at = dct["time"]
        if 'root_message' in dct:
            self.text = dct['root_message']
        else:
            self.text = dct['message']
        self.reposts_count = dct['forward_count']
        self.comments_count = dct['comment_count']
        self.username = dct['uid']
        self.usernick = ""
        
    def show(self):
        print "[%s] at %s \n  %s" % (self.username, self.created_at, self.text)
