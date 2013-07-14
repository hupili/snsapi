#-*- encoding: utf-8 -*-

'''
Renren Client

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
RENREN_API_SERVER = "https://api.renren.com/restserver.do"

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


class RenrenFeedMessage(snstype.Message):
    platform = "RenrenFeed"

    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.parsed.userid = dct['actor_id']
        self.parsed.username = dct['name']
        self.parsed.time = utils.str2utc(dct['update_time'], " +08:00")
        self.parsed.text = ""
        ORIG_USER = 'orig'
        if 'attachment' in dct and dct['attachment']:
            for at in dct['attachment']:
                if 'owner_name' in at and at['owner_name']:
                    ORIG_USER = at['owner_name']
                    self.parsed.username_orig = ORIG_USER
        if 'message' in dct:
            self.parsed.text += dct['message']
        if dct['feed_type'] in [21, 23, 32, 33, 36, 50, 51, 52, 53, 54, 55]:
            self.parsed.text += u"//" + ORIG_USER + ":"
        if dct['feed_type'] in [20, 21, 22, 23]:
            self.parsed.text += ' "' + dct['title'] + '" '
        if 'description' in dct:
            self.parsed.text += dct['description']
        if 'attachment' in dct and dct['attachment']:
            for at in dct['attachment']:
                if at['media_type'] == 'photo':
                    self.parsed.attachments.append(
                        {
                            'type': 'picture',
                            'format': ['link'],
                            #FIXME: page photo don't have raw_src
                            'data': 'raw_src' in at and at['raw_src'] or at['src']
                        }
                    )
                elif 'href' in at:
                    #FIXME: need to do some detailed handling
                    self.parsed.attachments.append(
                        {
                            'type': 'link',
                            'format': ['link'],
                            'data': at['href']
                        })


class RenrenFeed(SNSBase):

    Message = RenrenFeedMessage

    def __init__(self, channel = None):
        SNSBase.__init__(self, channel)

    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['app_key'] = ''
        c['app_secret'] = ''
        c['platform'] = 'RenrenFeed'
        c['auth_info'] = {
                "save_token_file": "(default)",
                "cmd_request_url": "(default)",
                "callback_url": "http://snsapi.ie.cuhk.edu.hk/aux/auth.php",
                "cmd_fetch_code": "(default)"
                }
        return c

    def renren_request(self, method=None, **kwargs):
        '''
        A general purpose encapsulation of renren API.
        It fills in system paramters and compute the signature.
        '''

        kwargs['method'] = method
        kwargs['access_token'] = self.token.access_token
        kwargs['v'] = '1.0'
        kwargs['format'] = 'json'
        kwargs['type'] = '10,11,20,21,22,23,30,31,32,33,34,35,36,40,41,50,51,52,53,54,55'
        response = self._http_post(RENREN_API_SERVER, kwargs)
        logger.debug('RESP: %s' % (response))


        if type(response) is not list and "error_code" in response:
            logger.warning(response["error_msg"])
            raise RenrenAPIError(response["error_code"], response["error_msg"])
        return response


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

        url = RENREN_AUTHORIZATION_URI + "?" + self._urlencode(args)
        self.request_url(url)

    def auth_second(self):
        '''
        docstring placeholder
        '''

        try:
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
        if not self.token:
            return False
        self.save_token()
        logger.debug("Authorized! access token is " + str(self.token))
        logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)

    def need_auth(self):
        return True

    @require_authed
    def home_timeline(self, count=20):
        #FIXME: automatic paging for count > 100
        api_params = dict()
        try:
            jsonlist = self.renren_request(
                method="feed.get",
                page=1,
                count=count
            )
        except RenrenAPIError, e:
            logger.warning("RenrenAPIError, %s", e)
            return snstype.MessageList()

        statuslist = snstype.MessageList()
        try:
            for j in jsonlist:
                statuslist.append(self.Message(
                    j,
                    platform = self.jsonconf['platform'],
                    channel = self.jsonconf['channel_name']
                ))
        except Exception, e:
            logger.warning("Catch exception: %s", e)

        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf['channel_name'])
        return statuslist
