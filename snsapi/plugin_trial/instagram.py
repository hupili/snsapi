if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
    import snspocket
    from snstype import BooleanWrappedData
    import platform
    import utils
    import time
    import urllib
    from third import instagram
else:
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from ..snstype import BooleanWrappedData
    from .. import snstype
    from .. import utils
    import time
    import urllib
    from ..third import instagram
INSTAGRAM_API1_SERVER = "https://api.instagram.com/v1/"

class InstagramMessage(snstype.Message):
    platform = "InstagramFeed"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.id = dct['id']

        self.parsed.time = utils.str2utc(dct['created_at'])
        #NOTE:
        #   * dct['user']['screen_name'] is the path part of user's profile URL.
        #   It is actually in a position of an id. You should @ this string in
        #   order to mention someone.
        #   * dct['user']['name'] is actually a nick name you can set. It's not
        #   permanent.
        self.parsed.username = dct['user']['screen_name']
        self.parsed.userid = dct['user']['id']
        self.parsed.text = dct['text']


class InstagramFeed(SNSBase):

    Message = InstagramMessage

    def __init__(self, channel = None):
        super(InstagramFeed, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.api = instagram.InstagramAPI(client_id=self.jsonconf["app_key"],\
                                client_secret=self.jsonconf["app_secret"],\
                                redirect_uri=self.jsonconf["auth_info"]["callback_url"])


    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'InstagramFeed'
        c['app_key'] = ''
        c['app_secret'] = ''
        c['auth_info'] = {
                "save_token_file": "(default)",
                "cmd_request_url": "(default)",
                "callback_url": "http://snsapi.sinaapp.com/auth.php",
                "cmd_fetch_code": "(default)"
                }
        return c

    def read_channel(self, channel):
        super(InstagramFeed, self).read_channel(channel)
        self.jsonconf['text_length_limit'] = 140

    def auth_first(self):
        '''
        docstring placeholder
        '''

        redirect_uri = self.api.get_authorize_login_url(scope = ["basic", "comments", "likes"])
        self.request_url(redirect_uri)
    def auth_second(self):
        '''
        docstring placeholder
        '''

        try:
            url = self.fetch_code()
            code = self._parse_code(url)
            (token, user_info) = self.api.exchange_code_for_access_token(code["code"])
            self.token = utils.JsonDict({"access_token": token, "user_info": user_info})
            self.token.expires_in = 86400 * 14 + self.time()
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None

    def auth(self):
        '''
        docstring placeholder
        '''
        try:
            if self.get_saved_token():
                return

            logger.info("Try to authenticate '%s' using OAuth2", self.jsonconf.channel_name)
            self.auth_first()
            self.auth_second()
            if not self.token:
                return False
            self.save_token()
            logger.debug("Authorized! access token is " + str(self.token))
            logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)
        except Exception,e:
            logger.warning("Auth second fail. Catch exception: %s", e)

    def need_auth(self):
        return True
		
    def instagram_request(self, resource, method="get", **kwargs):
        return self._instagram_request_v1(resource, method.lower(), **kwargs)

    def _instagram_request_v1(self, resource, method="get", **kwargs):
        '''
        A general purpose encapsulation of renren API.
        It fills in system paramters and compute the signature.
        Return a list on success
        raise Exception on error
        '''

        kwargs['access_token'] = self.token.access_token
        response = eval("self._http_" + method)(INSTAGRAM_API1_SERVER + resource, kwargs)
        logger.warning(str(response))
        
        if type(response) is not list and "error_type" in response:
            logger.warning(response)
            self.auth()
            return self._instagram_request_v1(method, resource, kwargs)
        return response
    
     
    @require_authed
    def home_timeline(self, count = 20):
        '''
        NOTE: this does not include your re-tweeted statuses.
        It's another interface to get re-tweeted status on Tiwtter.
        We'd better save a call.
        Deprecate the use of retweets.
        See reply and forward of this platform for more info.
        '''
 
        try:
            jsonlist = self.instagram_request(
                resource="users/self/feed",
                method="get",
                count=count
            )
        except Exception, e:
            logger.warning("InstagramAPIError, %s", e)
            return snstype.MessageList()
        #statuslist = snstype.MessageList()
        #for j in jsonlist:
        #    try:
        #        statuslist.append(self.Message(
        #            j,
        #            platform = self.jsonconf['platform'],
        #            channel = self.jsonconf['channel_name']
        #        ))
        #    except Exception, e:
        #        logger.warning("Catch exception: %s", e)
        #
        #logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf['channel_name'])
        #return statuslist

    def update(self, text):
        logger.warning("Instagram does not support update()!")
        return False
        
    @require_authed
    def reply(self, statusID, text):
        text = self._cat(self.jsonconf['text_length_limit'], [(text, 1)])
        try:
            status = self.api.PostUpdate(text,
                                         in_reply_to_status_id=statusID.id)
            #TODO:
            #     Find better indicator for status update success
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Instagram failed: %s', str(e))
            return False

    def forward(self, message, text):
        logger.warning("Instagram does not support update()!")
        return False
        
    def expire_after(self, token = None):
        # This platform does not have token expire issue.
        return -1

class InstagramSearchMessage(InstagramMessage):
    platform = "InstagramSearch"

class InstagramSearch(InstagramFeed):
    Message = InstagramSearchMessage

    @staticmethod
    def new_channel(full=False):
        c = InstagramFeed.new_channel(full)
        c['platform'] = 'InstagramSearch'
        c['term'] = 'snsapi'
        c['include_entities'] = True
        return c

    def __init__(self, channel = None):
        super(InstagramSearch, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.api = InstagramAPI(client_id=self.jsonconf["app_key"],\
                                client_secret=self.jsonconf["secret"],\
                                redirect_uri=self.jsonconf["auth_info"]["callback_url"])

    def home_timeline(self, count = 20):
        status_list = snstype.MessageList()
        try:
            #statuses = self.api.GetHomeTimeline(count = count)
            statuses = self.api.GetSearch(term=self.jsonconf['term'],
                            include_entities=self.jsonconf['include_entities'],
                            count=count)
            for s in statuses:
                status_list.append(self.Message(s.AsDict(),\
                        self.jsonconf['platform'],\
                        self.jsonconf['channel_name']))
            logger.info("Read %d statuses from '%s'", len(status_list), self.jsonconf['channel_name'])
        except Exception, e:
            logger.warning("Catch expection: %s", e)
        return status_list
        
if __name__ == '__main__':

    nc = InstagramFeed.new_channel()
    nc["app_key"] = "7e6bee26ee644ae3b1ba3e3f6dfd8995"
    nc["app_secret"] = "8187653262324c339cc2cce80ff2f114"
    nc["auth_info"]["callback_url"] = "http://snsapi.sinaapp.com/auth.php"
    nc["platform"] = "RenrenFeed"
    nc["channel_name"] = "wcyz"
    insta = InstagramFeed(nc)
    insta.auth()
    insta.home_timeline()

    
