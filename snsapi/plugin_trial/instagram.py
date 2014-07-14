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
    from third import instagram as insta
else:
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from ..snstype import BooleanWrappedData
    from .. import snstype
    from .. import utils
    import time
    import urllib
    from ..third import instagram as insta

INSTAGRAM_API1_SERVER = "https://api.instagram.com/v1/"

# This error is moved back to "Instagram.py".
# It's platform specific and we do not expect other
# file to raise this error.
class InstagramAPIError(Exception):
    def __init__(self, code, message):
        super(InstagramAPIError, self).__init__(message)
        self.code = code


class InstagramMessage(snstype.Message):

    platform = "InstagramFeed"

    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, data):
        self.ID.status_id = data['id']
        self.ID.id = data['id']
        self.ID.source_user_id = self.parsed.userid = str(data['user']['id'])
        self.parsed.time = float(data['created_time'])
        self.parsed.attachments.append(
                    {
                        'type': 'picture',
                        'format': ['link'],
                        # FIXME: page photo don't have raw_src
                        'data': data["images"]["standard_resolution"]["url"]
                    }
                )
        # NOTE:
        #   * dct['user']['screen_name'] is the path part of user's profile URL
        #   It is actually in a position of an id. You should @ this string in
        #   order to mention someone.
        #   * dct['user']['name'] is actually a nick name you can set. It's not
        #   permanent.
        self.parsed.username = data['user']['username']
        self.parsed.liked = data["user_has_liked"]
        try:
            self.parsed.text = data['caption']['text']
        except Exception, e:
            self.parsed.text = ""


class InstagramFeed(SNSBase):

    Message = InstagramMessage

    def __init__(self, channel=None):
        super(InstagramFeed, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.api = insta.InstagramAPI(client_id=self.jsonconf["app_key"],
                                client_secret=self.jsonconf["app_secret"],
                                redirect_uri=self.jsonconf["auth_info"]["callback_url"])

    @staticmethod
    def new_channel(full=False):
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

        redirect_uri = self.api.get_authorize_login_url(scope=["basic", "comments", "likes"])
        self.request_url(redirect_uri)

    def auth_second(self):
        '''
        docstring placeholder
        '''
        # NOTE:
        # Instagram API will not return any info related to the 
        # expiration data. Accordian to its document, the expiration
        # data is uncertain. Instagram makes no guarantee on it thus
        # we set it to two weeks (86400 * 14)
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
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)

    def need_auth(self):
        return True

    def instagram_request(self, resource, method="get", **kwargs):
        return self._instagram_request_v1(resource, method.lower(), **kwargs)

    def _instagram_request_v1(self, resource, method="get", **kwargs):
        '''
        A general purpose encapsulation of instagram API.
        It fills in system paramters and compute the signature.
        Return a list on success
        raise Exception on error
        '''

        kwargs['access_token'] = self.token.access_token
        response = eval("self._http_" + method)(INSTAGRAM_API1_SERVER + resource, kwargs)

        if "error_type" in response['meta']:
            if response['meta']["error_type"] == "OAuthParameterException":
                logger.warning(response)
                self.auth()
                return self._instagram_request_v1(method, resource, kwargs)
            else:
                raise InstagramAPIError(response['meta']["error_message"])
        return response

    @require_authed
    def home_timeline(self, count=20):

        try:
            jsonlist = self.instagram_request(
                resource="users/self/feed",
                method="get",
                count=count
            )
        except Exception, e:
            logger.warning("InstagramAPIError, %s", e)
            return snstype.MessageList()
        statuslist = snstype.MessageList()
        for j in jsonlist["data"]:
            try:
                statuslist.append(self.Message(
                    j,
                    platform=self.jsonconf['platform'],
                    channel=self.jsonconf['channel_name']
                ))
            except Exception, e:
                logger.warning("Catch exception: %s", e)

        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf['channel_name'])
        return statuslist

    def update(self, text):
        logger.warning("Instagram does not support update()!")
        return False

    # NOTE:
    # Comments function will be blocked by Instagram by default.
    # Anyone who would like to use this function must
    # apply for authorization first. Refer to the following website:
    # https://help.instagram.com/contact/185819881608116
    @require_authed
    def reply(self, statusID, text):
        try:
            result = self.instagram_request(
                    resource="media/" + statusID + "/comments",
                    method="post",
                    text=text
                )
            # TODO:
            #     Find better indicator for status update success
            return True
        except Exception, e:
            logger.warning('update Instagram failed: %s', str(e))
            return False

    @require_authed
    def like(self, message):
        if str(message.parsed.liked).lower() == "true":
            logger.warning("You have liked this message before")
            return True
        else:
            try:
                jsonlist = self.instagram_request(
                    resource="media/" + message.ID.id + "/likes",
                    method="post"
                )
                message.parsed.liked = True
                return True
            except Exception, e:
                logger.warning("InstagramAPIError, %s", e)
                return False

    @require_authed
    def unlike(self, message):
        if str(message.parsed.liked).lower() == "false":
            logger.warning("You have never liked this message before")
            return True
        else:
            try:
                jsonlist = self.instagram_request(
                    resource="media/" + message.ID.id + "/likes",
                    method="delete"
                )
                message.parsed.liked = False
                return True
            except Exception, e:
                logger.warning("InstagramAPIError, %s", e)
                return False

    def forward(self, message, text):
        logger.warning("Instagram does not support update()!")
        return False
