#-*- encoding: utf-8 -*-

'''
renren-share client
'''

from ..snslog import SNSLog
logger = SNSLog
from ..snsapi import SNSAPI
from ..snstype import Status,User,Error
from .. import errors
from ..utils import console_output

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

logger.debug("%s plugged!", __file__)

# Inteface URLs.
# This differs from other platforms
RENREN_AUTHORIZATION_URI = "http://graph.renren.com/oauth/authorize"
RENREN_ACCESS_TOKEN_URI = "http://graph.renren.com/oauth/token"
RENREN_SESSION_KEY_URI = "http://graph.renren.com/renren_api/session_key"
RENREN_API_SERVER = "http://api.renren.com/restserver.do"

class RenrenShareAPI(SNSAPI):
    def __init__(self, channel = None):
        super(RenrenShareAPI, self).__init__()
        
        self.platform = "renren_share"
        self.domain = "graph.renren.com"
        self.app_key = ""
        self.app_secret = ""
        self.auth_info.callback_url = "http://graph.renren.com/oauth/login_success.html"
        if channel:
            self.read_channel(channel)

    def read_channel(self, channel):
        super(RenrenShareAPI, self).read_channel(channel) 

        self.channel_name = channel['channel_name']
        self.app_key = channel['app_key']
        self.app_secret = channel['app_secret']
        
    def auth_first(self):
        args = dict(client_id=self.app_key, redirect_uri = self.auth_info.callback_url)
        args["response_type"] = "code"
        args["scope"] = "read_user_status status_update publish_comment"
        args["state"] = "snsapi! Stand up, Geeks! Step on the head of those evil platforms!"
        url = RENREN_AUTHORIZATION_URI + "?" + self._urlencode(args)
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
        self.token.update(self._http_get(RENREN_ACCESS_TOKEN_URI, args))
        self.token.expires_in = self.token.expires_in + time.time()

    def auth(self):
        if self.get_saved_token():
            return

        logger.info("Try to authenticate '%s' using OAuth2", self.channel_name)
        self.auth_first()
        self.auth_second()
        self.save_token()
        logger.debug("Authorized! access token is " + str(self.token))
        logger.info("Channel '%s' is authorized", self.channel_name)

    def renren_request(self, params = None):
        """
        A general purpose encapsulation of renren API. 
        It fills in system paramters and compute the signature. 
        """

        #request a session key
        session_key_request_args = {"oauth_token": self.token.access_token}
        response = self._http_get(RENREN_SESSION_KEY_URI, session_key_request_args)
        session_key = str(response["renren_token"]["session_key"])

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
        
        try:
            response = self._http_post(RENREN_API_SERVER, params)
        finally:
            pass

        if type(response) is not list and "error_code" in response:
            logger.warning(response["error_msg"]) 
            raise errors.RenRenAPIError(response["error_code"], response["error_msg"])
        return response

    def __hash_params(self, params = None):
        hashstring = "".join(["%s=%s" % (self._unicode_encode(x), self._unicode_encode(params[x])) for x in sorted(params.keys())])
        hashstring = hashstring + self._unicode_encode(self.app_secret)
        #logger.debug(hashstring)
        hasher = hashlib.md5(hashstring)
        return hasher.hexdigest()
        
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''

        #api_params = dict(method = "feed.get", type = 10, page = 1, count = count)
        api_params = dict(method = "feed.get", \
                type = "21,32,33,50,51,52", \
                page = 1, count = count)
        jsonlist = self.renren_request(api_params)
        
        statuslist = []
        for j in jsonlist:
            statuslist.append(RenrenShareStatus(j))

        logger.info("Read %d statuses from '%s'", len(statuslist), self.channel_name)
        return statuslist

    #def update(self, text):
    #    '''update a status
    #    @param text: the update message
    #    @return: success or not
    #    '''

    #    api_params = dict(method = "status.set", status = text)
    #    
    #    try:
    #        ret = self.renren_request(api_params)
    #        if 'result' in ret and ret['result'] == 1:
    #            logger.info("Update status '%s' on '%s' succeed", text, self.channel_name)
    #            return True
    #    except:
    #        pass

    #    logger.info("Update status '%s' on '%s' fail", text, self.channel_name)
    #    return False

    def reply(self, statusID, text):
        """reply status
        @param status: StatusID object
        @param text: string, the reply message
        @return: success or not
        """

        #TODO: check platform and place a warning
        #      if it is not "renren"

        #api_params = dict(method = "status.addComment", content = text, \
        api_params = dict(method = "share.addComment", content = text, \
            share_id = statusID.status_id, user_id = statusID.source_user_id)
            #status_id = statusID.status_id, owner_id = statusID.source_user_id)

        try:
            ret = self.renren_request(api_params)
            if 'result' in ret and ret['result'] == 1:
                logger.info("Reply '%s' to status '%s' succeed", text, statusID)
                return True
        except:
            pass

        logger.info("Reply '%s' to status '%s' fail", text, statusID)
        return False

        
#TODO: 
#    "Status" is not an abstract enough word. 
#    Suggested to change it to "Message". 
#    There are many types of messages on renren. 
#    There are even many types for new feeds alone. 
#    Ref: http://wiki.dev.renren.com/wiki/Type%E5%88%97%E8%A1%A8
class RenrenShareStatus(Status):
    def parse(self, dct):
        self.ID.platform = "renren_share"
        self._parse_feed_share(dct)

    def _parse_feed_share(self, dct):
        #logger.debug(json.dumps(dct))
        #By trial, it seems:
        #   * 'post_id' : the id of news feeds
        #   * 'source_id' : the id of status
        #     equal to 'status_id' returned by 
        #     'status.get' interface
        #self.id = dct["post_id"]
        self.id = dct["source_id"]
        self.created_at = dct["update_time"]
        #self.text = dct['message']
        #self.text = dct['content']
        #self.text = dct['text']
        #self.text = dct['source_text']
        self.text = dct['message'] + " --> " + dct['description']
        self.reposts_count = 'N/A'
        self.comments_count = dct['comments']['count']
        self.username = dct['name']
        self.usernick = ""
        self.ID.status_id = dct["source_id"]
        self.ID.source_user_id = dct["actor_id"]

    #def show(self):
    #    print self.ID

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

