#-*- encoding: utf-8 -*-

'''
Renren Client

Codes are adapted from following sources:
   * http://wiki.dev.renren.com/mediawiki/images/4/4c/Renren-oauth-web-demo-python-v1.0.rar
'''

if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
    from utils import console_output
    import utils
else:
    import sys
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from .. import snstype
    from ..utils import console_output
    from .. import utils


logger.debug("%s plugged!", __file__)

# Inteface URLs.
# This differs from other platforms
RENREN_AUTHORIZATION_URI = "http://graph.renren.com/oauth/authorize"
RENREN_ACCESS_TOKEN_URI = "http://graph.renren.com/oauth/token"
RENREN_SESSION_KEY_URI = "http://graph.renren.com/renren_api/session_key"
RENREN_API_SERVER = "http://api.renren.com/restserver.do"

# This error is moved back to "renren.py". 
# It's platform specific and we do not expect other 
# file to raise this error. 
class RenrenAPIError(Exception):
    def __init__(self, code, message):
        super(RenrenAPIError, self).__init__(message)
        self.code = code

class RenrenBase(SNSBase):
    def __init__(self, channel = None):
        super(RenrenBase, self).__init__(channel)
        self.platform = self.__class__.__name__

    @staticmethod
    def new_channel(full = False):
        '''
        docstring placeholder
        '''

        c = SNSBase.new_channel(full)

        c['app_key'] = ''
        c['app_secret'] = ''
        c['platform'] = 'RenrenBase'
        c['auth_info'] = {
                "save_token_file": "(default)", 
                "cmd_request_url": "(default)", 
                "callback_url": "http://snsapi.sinaapp.com/auth.php", 
                "cmd_fetch_code": "(default)" 
                } 

        return c

        
    def read_channel(self, channel):
        '''
        docstring placeholder
        '''

        super(RenrenBase, self).read_channel(channel) 

        if not "callback_url" in self.auth_info: 
            self.auth_info.callback_url = "http://snsapi.sinaapp.com/auth.php"
            # The following is official test link. 
            # Keep here for future reference. 
            #self.auth_info.callback_url = "http://graph.renren.com/oauth/login_success.html"

        # Renren API document says the limit is 140 character....
        # After test, it seems 245 unicode character. 
        # To leave some safe margin, we use 240 here. 
        self.jsonconf['text_length_limit'] = 240
        
        #if not 'platform_prefix' in self.jsonconf:
        #    self.jsonconf['platform_prefix'] = u'人人'

    def need_auth(self):
        '''
        docstring placeholder
        '''

        return True
        
    def auth_first(self):
        '''
        docstring placeholder
        '''

        args = {"client_id": self.jsonconf.app_key, 
                "redirect_uri": self.auth_info.callback_url}
        args["response_type"] = "code"
        args["scope"] = " ".join(["read_user_feed",
                                  "read_user_status",
                                  "read_user_blog",
                                  "status_update",
                                  "publish_comment",
                                  "publish_blog"])

        #TODO:
        #    The "state" param is used to synchronize between SNS and
        #    the app. More concious use of it is generally needed.
        #    Since SNSAPI is targeted for developer user who apply keys
        #    and deploy it themselves, there is little problem.
        args["state"] = "snsapi! Stand up, Geeks! Step on the head of those evil platforms!"
        url = RENREN_AUTHORIZATION_URI + "?" + self._urlencode(args)
        self.request_url(url)

    def auth_second(self):
        '''
        docstring placeholder
        '''

        try:
            #TODO:
            #    The name 'fetch_code' is not self-explained.
            #    It actually fetches the authenticated callback_url.
            #    Code is parsed from this url. 
            url = self.fetch_code()
            self.token = self._parse_code(url)
            args = dict(client_id=self.jsonconf.app_key, redirect_uri = self.auth_info.callback_url)
            args["client_secret"] = self.jsonconf.app_secret
            args["code"] = self.token.code
            args["grant_type"] = "authorization_code"
            self.token.update(self._http_get(RENREN_ACCESS_TOKEN_URI, args))
            self.token.expires_in = self.token.expires_in + self.time()
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None

    def auth(self):
        '''
        docstring placeholder
        '''

        if self.get_saved_token():
            return

        logger.info("Try to authenticate '%s' using OAuth2", self.jsonconf.channel_name)
        self.auth_first()
        self.auth_second()
        self.save_token()
        logger.debug("Authorized! access token is " + str(self.token))
        logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)

    def renren_request(self, params = None):
        '''
        A general purpose encapsulation of renren API. 
        It fills in system paramters and compute the signature. 
        '''

        #request a session key
        try:
            session_key_request_args = {"oauth_token": self.token.access_token}
            response = self._http_get(RENREN_SESSION_KEY_URI, session_key_request_args)
            session_key = str(response["renren_token"]["session_key"])
        except Exception, e:
            logger.warning("Catch exception when requesting session key: %s", e)
            if type(response) is not list and "error_code" in response:
                logger.warning(response["error_msg"]) 
                raise RenrenAPIError(response["error_code"], response["error_msg"])
            return []

        #system parameters fill-in
        params["api_key"] = self.jsonconf.app_key
        params["call_id"] = str(int(self.time() * 1000))
        params["format"] = "json"
        params["session_key"] = session_key
        params["v"] = '1.0'
        # del 'sig' first, if not:
        #   Client may use the same params dict repeatedly. 
        #   Later call will fail because they have previous 'sig'. 
        if "sig" in params:
            del params["sig"] 
        sig = self.__hash_params(params);
        params["sig"] = sig
        
        try:
            response = self._http_post(RENREN_API_SERVER, params)
        except Exception, e:
            logger.warning("Catch exception: %s", e)

        if type(response) is not list and "error_code" in response:
            logger.warning(response["error_msg"]) 
            raise RenrenAPIError(response["error_code"], response["error_msg"])
        return response

    def __hash_params(self, params = None):
        import hashlib
        hashstring = "".join(["%s=%s" % (self._unicode_encode(x), self._unicode_encode(params[x])) for x in sorted(params.keys())])
        hashstring = hashstring + self._unicode_encode(self.jsonconf.app_secret)
        hasher = hashlib.md5(hashstring)
        return hasher.hexdigest()
        

class RenrenShareMessage(snstype.Message):
    platform = "RenrenShare"

    def parse(self):
        self.ID.platform = self.platform
        self._parse_feed_share(self.raw)

    def _parse_feed_share(self, dct):
        self.ID.status_id = dct["source_id"]
        self.ID.source_user_id = dct["actor_id"]

        self.parsed.userid = dct['actor_id']
        self.parsed.username = dct['name']
        self.parsed.time = utils.str2utc(dct["update_time"], " +08:00")

        if dct['feed_type'] == 33:
            self._parse_feed_33(dct)
        elif dct['feed_type'] == 32:
            self._parse_feed_32(dct)
        else:
            #self.parsed.text_orig = dct['description']
            self.parsed.text_last = dct['message'] 
            self.parsed.text_trace = dct['trace']['text']
            self.parsed.title = dct['title']
            self.parsed.description = dct['description']
            self.parsed.reposts_count = 'N/A'
            self.parsed.comments_count = dct['comments']['count']
            self.parsed.text_orig = self.parsed.title + "||" + self.parsed.description
            # Assemble a general format message
            self.parsed.text = self.parsed.text_trace \
                    + "||" + self.parsed.title \
                    + "||" + self.parsed.description

    def _parse_feed_33(self, dct):
        '''
        Feed type 33. Albums 
        '''

        #self.parsed.text_orig = dct['prefix']
        self.parsed.text_last = dct['message'] 
        self.parsed.text_trace = dct['trace']['text']
        self.parsed.title = dct['title']
        self.parsed.link = dct['href']
        self.parsed.description = dct['title']
        self.parsed.reposts_count = 'N/A'
        self.parsed.comments_count = dct['comments']['count']
        self.parsed.text_orig = self.parsed.title + "||" + self.parsed.link

        #self.parsed.text = "%s||%s||%s" % (\
        #        self.parsed.text_orig, self.parsed.title, self.parsed.link)
        self.parsed.text = "%s||%s" % (\
                self.parsed.title, self.parsed.link)

    def _parse_feed_32(self, dct):
        '''
        Feed type 33. Photo
        '''

        #self.parsed.text_orig = dct['description']
        self.parsed.text_last = dct['message'] 
        self.parsed.text_trace = dct['trace']['text']
        self.parsed.title = dct['title']
        self.parsed.link = dct['attachment'][0]['href']
        self.parsed.description = dct['description']
        self.parsed.reposts_count = 'N/A'
        self.parsed.comments_count = dct['comments']['count']
        self.parsed.text_orig = self.parsed.link + "||" + self.parsed.title + "||" + self.parsed.description

        self.parsed.text = "%s||%s||%s||%s" % (\
                self.parsed.text_trace, self.parsed.link, self.parsed.title, self.parsed.description)


class RenrenShare(RenrenBase):

    Message = RenrenShareMessage

    def __init__(self, channel = None):
        super(RenrenShare, self).__init__(channel)
        self.platform = self.__class__.__name__

    @staticmethod
    def new_channel(full = False):
        '''
        docstring placeholder

        '''

        c = RenrenBase.new_channel(full)
        c['platform'] = 'RenrenShare'
        return c
        
    @require_authed
    def home_timeline(self, count=20):
        '''
        Get timeline of Renren statuses

        :param count: 
            Number of statuses

        :return:
            At most ``count`` statuses (can be less).
        '''

        api_params = dict(method = "feed.get", \
                type = "21,32,33,50,51,52", \
                page = 1, count = count)
        try:
            jsonlist = self.renren_request(api_params)
        except RenrenAPIError, e:
            logger.warning("RenrenAPIError, %s", e)
            return snstype.MessageList()
        
        statuslist = snstype.MessageList()
        try:
            for j in jsonlist:
                statuslist.append(self.Message(j,\
                        platform = self.jsonconf['platform'],\
                        channel = self.jsonconf['channel_name']\
                        ))
        except Exception, e:
            logger.warning("Catch expection: %s", e)

        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf.channel_name)
        return statuslist

    @require_authed
    def reply(self, statusID, text):
        '''
        docstring placeholder
        '''

        #"""reply status
        #@param status: StatusID object
        #@param text: string, the reply message
        #@return: success or not
        #"""

        api_params = dict(method = "share.addComment", content = text, \
            share_id = statusID.status_id, user_id = statusID.source_user_id)

        try:
            ret = self.renren_request(api_params)
            logger.debug("Reply to status '%s' return: %s", statusID, ret)
            if 'result' in ret and ret['result'] == 1:
                logger.info("Reply '%s' to status '%s' succeed", text, statusID)
                return True
            else:
                return False
        except Exception, e:
            logger.warning("Reply failed: %s", e)

        logger.info("Reply '%s' to status '%s' fail", text, statusID)
        return False

class RenrenStatusMessage(snstype.Message):
    platform = "RenrenStatus"
    def parse(self):
        self.ID.platform = self.platform
        self._parse_feed_status(self.raw)

    def _parse_feed_status(self, dct):
        #logger.debug(json.dumps(dct))
        # By trial, it seems:
        #    * 'post_id' : the id of news feeds
        #    * 'source_id' : the id of status
        #      equal to 'status_id' returned by 
        #      'status.get' interface
        # self.id = dct["post_id"]

        self.ID.status_id = dct["source_id"]
        self.ID.source_user_id = dct["actor_id"]

        self.parsed.userid = dct['actor_id']
        self.parsed.username = dct['name']
        self.parsed.time = utils.str2utc(dct["update_time"], " +08:00")
        self.parsed.text = dct['message']

        #print dct 

        try:
            self.parsed.username_orig = dct['attachment'][0]['owner_name']
            self.parsed.text_orig = dct['attachment'][0]['content']
            self.parsed.text += " || " + "@" + self.parsed.username_orig \
                    + " : " + self.parsed.text_orig
            #print self.parsed.text
        except:
            pass
        #except Exception, e:
        #    raise e

        self.parsed.text_trace = dct['message'] 
        self.parsed.reposts_count = 'N/A'
        self.parsed.comments_count = dct['comments']['count']

        #self.parsed.id = dct["source_id"]
        #self.parsed.created_at = dct["update_time"]
        #self.parsed.text = dct['message']
        #self.parsed.reposts_count = 'N/A'
        #self.parsed.comments_count = dct['comments']['count']
        #self.parsed.username = dct['name']
        #self.parsed.usernick = ""
        #self.ID.status_id = dct["source_id"]
        #self.ID.source_user_id = dct["actor_id"]

    # The following is to parse Status of Renren. 
    # (get by invoking 'status.get', not 'feed.get')
    #def _parse_status(self, dct):
    #    self.id = dct["status_id"]
    #    self.created_at = dct["time"]
    #    if 'root_message' in dct:
    #        self.text = dct['root_message']
    #    else:
    #        self.text = dct['message']
    #    self.reposts_count = dct['forward_count']
    #    self.comments_count = dct['comment_count']
    #    self.username = dct['uid']
    #    self.usernick = ""

class RenrenStatus(RenrenBase):
    Message = RenrenStatusMessage
    def __init__(self, channel = None):
        super(RenrenStatus, self).__init__(channel)
        self.platform = self.__class__.__name__
        
    @staticmethod
    def new_channel(full = False):
        c = RenrenBase.new_channel(full)
        c['platform'] = 'RenrenStatus'
        return c
        
    @require_authed
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''

        api_params = dict(method = "feed.get", type = 10, page = 1, count = count)
        
        statuslist = snstype.MessageList()
        try:
            jsonlist = self.renren_request(api_params)
            for j in jsonlist:
                statuslist.append(self.Message(j,\
                        platform = self.jsonconf['platform'],\
                        channel = self.jsonconf['channel_name']\
                        ))
        except Exception, e:
            logger.warning("catch expection:%s", e.message)

        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf.channel_name)
        return statuslist

    @require_authed
    def update(self, text):
        '''update a status
        @param text: the update message
        @return: success or not
        '''

        text = self._cat(self.jsonconf['text_length_limit'], [(text,1)])

        api_params = dict(method = "status.set", status = text)
        
        try:
            ret = self.renren_request(api_params)
            if 'result' in ret and ret['result'] == 1:
                logger.info("Update status '%s' on '%s' succeed", text, self.jsonconf.channel_name)
                return True
        except Exception, e:
            logger.warning("Catch Exception %s", e)

        logger.info("Update status '%s' on '%s' fail", text, self.jsonconf.channel_name)
        return False

    @require_authed
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
                logger.info("Reply '%s' to status '%s' succeed", text, statusID)
                return True
        except Exception, e:
            logger.warning("Catch Exception %s", e)

        logger.info("Reply '%s' to status '%s' fail", text, statusID)
        return False

class RenrenBlogMessage(snstype.Message):

    platform = "RenrenBlog"

    def parse(self):
        self.ID.platform = self.platform
        self._parse_feed_blog(self.raw)

    def _parse_feed_blog(self, dct):
        self.ID.feed_id = dct["post_id"]
        self.ID.user_type = dct["actor_type"]
        self.ID.blog_id = dct["source_id"]
        if dct["actor_type"] == "user":
            self.ID.source_user_id = dct["actor_id"]
        else:  #page
            self.ID.source_page_id = dct["actor_id"]

        self.parsed.userid = dct['actor_id']
        self.parsed.username = dct['name']
        self.parsed.time = utils.str2utc(dct["update_time"], " +08:00")
        # This is the news feed of blogs, so you can not get the body
        self.parsed.description = dct['description']
        self.parsed.text = dct['description']
        self.parsed.title = dct['title']

class RenrenBlog(RenrenBase):

    Message = RenrenBlogMessage

    def __init__(self, channel = None):
        super(RenrenBlog, self).__init__(channel)
        self.platform = self.__class__.__name__
        
    @staticmethod
    def new_channel(full = False):
        c = RenrenBase.new_channel(full)
        c['platform'] = 'RenrenBlog'
        return c
        
    @require_authed
    def home_timeline(self, count=20):
        '''
        Get blog timeline

        :param count: Number of blogs
        '''

        api_params = {'method': 'feed.get',
                      'type': '20,22',
                      'page': 1, 
                      'count': count}

        try:
            jsonlist = self.renren_request(api_params)
            logger.debug("Get %d elements in response", len(jsonlist))
        except RenrenAPIError, e:
            logger.warning("RenrenAPIError, %s", e)
            return snstype.MessageList()
        
        statuslist = snstype.MessageList()
        try:
            for j in jsonlist:
                statuslist.append(self.Message(j,
                        platform = self.jsonconf['platform'],
                        channel = self.jsonconf['channel_name']
                        ))
        except Exception, e:
            logger.warning("Catch expection: %s", e)

        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf.channel_name)
        return statuslist


    @require_authed
    def update(self, text, title=None):
        '''
        Post a blog

        :param text: Blog post body.
        :param title: Blog post title. (optional)
        :return: success or not
        '''

        if title is None:
            title = self._cat(20, [(text, 1)])

        api_params = {'method': 'blog.addBlog', 
                      'content': text,
                      'title': title}
        
        try:
            ret = self.renren_request(api_params)
            logger.debug("response: %s", ret)
            #TODO:
            #    Preserve the id for further use? 
            #    Return it as multi-return-value? 
            if 'id' in ret:
                logger.info("Update status '%s' on '%s' succeed", text, self.jsonconf.channel_name)
                return True
        except Exception, e:
            logger.warning("Catch Exception %s", e)

        logger.info("Update status '%s' on '%s' fail", text, self.jsonconf.channel_name)
        return False

    @require_authed
    def reply(self, mID, text):
        '''
        Reply a renren blog

        :param mID: MessageID object
        :param text: string, the reply message
        :return: success or not
        '''

        if mID.user_type == 'user':
            owner_key = 'uid'
            owner_value = mID.source_user_id
        else:  # 'page'
            owner_key = 'page_id'
            owner_value = mID.source_page_id

        api_params = {'method': 'blog.addComment',
                      'content': text,
                      'id': mID.blog_id, 
                      owner_key: owner_value}

        logger.debug('request parameters: %s', api_params)

        try:
            ret = self.renren_request(api_params)
            if 'result' in ret and ret['result'] == 1:
                logger.info("Reply '%s' to status '%s' succeed", text, mID)
                return True
        except Exception, e:
            logger.warning("Catch Exception %s", e)

        logger.info("Reply '%s' to status '%s' fail", text, mID)
        return False


if __name__ == '__main__':
    print '\n\n\n'
    print '==== SNSAPI Demo of renren.py module ====\n'
    # Create and fill in app information
    renren_conf = RenrenStatus.new_channel()
    renren_conf['channel_name'] = 'test_renren'
    renren_conf['app_key'] = '1c62fea4599e420fb4ac2a1fe38cc546'     # Chnage to your own keys
    renren_conf['app_secret'] = '151655bf6c87414e8571da69d8d7bd40'  # Change to your own keys
    # Instantiate the channel
    renren = RenrenStatus(renren_conf)
    # OAuth your app
    print 'SNSAPI is going to authorize your app.'
    print 'Please make sure:'
    print '   * You have filled in your own app_key and app_secret in this script.'
    print '   * You configured the callback_url on dev.renren.com as'
    print '     http://snsapi.sinaapp.com/auth.php'
    print 'Press [Enter] to continue or Ctrl+C to end.'
    raw_input()
    renren.auth()
    # Test get 2 messages from your timeline
    status_list = renren.home_timeline(2)
    print '\n\n--- Statuses of your friends is followed ---'
    print status_list
    print '--- End of status timeline ---\n\n'

    print 'Short demo ends here! You can do more with SNSAPI!'
    print 'Please join our group for further discussions'
