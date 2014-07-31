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
    from third import douban_client as doubansdk
    import json
else:
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from ..snstype import BooleanWrappedData
    from .. import snstype
    from .. import utils
    import time
    import urllib
    from ..third import douban_client as doubansdk
    import json


# This error is moved back to "douban.py".
# It's platform specific and we do not expect other
# file to raise this error.
class DoubanAPIError(Exception):
    def __init__(self, code, message):
        super(DoubanAPIError, self).__init__(message)
        self.code = code


class DoubanMessage(snstype.Message):

    platform = "DoubanFeed"

    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, data):
        self.ID.status_id = data['id']
        self.ID.id = data['id']
        self.ID.source_user_id = self.parsed.userid = str(data['user']['id'])
        self.parsed.time = utils.str2utc(data['created_at'], " +08:00")
        self.parsed.text = data['title'] + u"   "
        self.parsed.text += data['text']
        self.parsed.username = data['user']['screen_name']
        if hasattr(data, 'reshared_status'):
            self.parsed.text += u"// " + data['reshared_status']['user']['screen_name'] + self._get_share_text(data['reshared_status'])
        if data['attachments']:
            for at in data['attachments']:
                if str(at['type']) in ['image', 'photos']:
                    for at1 in at['media']:
                        self.parsed.attachments.append(
                            {
                                'type': 'picture',
                                'format': ['link'],
                                # FIXME: page photo don't have raw_src
                                'data': at1['src'].replace("small", "raw", 1)
                            }
                        )
                else:
                    self.parsed.text += at['title'] + u" : " + at['description']
                    self.parsed.attachments.append(
                            {
                                'type': at['type'],
                                'format': ['link'],
                                'data': at['expaned_href']
                            })

    def _get_share_text(self, data):
        text = data['title'] + u" : "
        text += data['text']
        if hasattr(data, 'reshared_status'):
            text += u"// " + data['reshared_status']['user']['screen_name'] + self._get_share_text(data['reshared_status'])
        if data['attachments'] and data['has_photo'] != True:
            for at in data['attachments']:
                if at['description'] != "":
                    text += at['description']
                else:
                    text += at['title']
        return text


class DoubanFeed(SNSBase):

    Message = DoubanMessage

    def __init__(self, channel=None):
        super(DoubanFeed, self).__init__(channel)
        self.platform = self.__class__.__name__

        SCOPE = 'douban_basic_common,shuo_basic_r,shuo_basic_w,community_advanced_doumail_r'
        self.client = doubansdk.DoubanClient(self.jsonconf["app_key"],
                              self.jsonconf["app_secret"],
                              self.jsonconf["auth_info"]["callback_url"],
                              SCOPE)

    @staticmethod
    def new_channel(full=False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'DoubanFeed'
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
        super(DoubanFeed, self).read_channel(channel)

    def auth_first(self):
        '''
        docstring placeholder
        '''
        self.request_url(self.client.authorize_url)

    def auth_second(self):
        '''
        docstring placeholder
        '''
        # NOTE:
        # Accordion to Douban API, the token will expire
        # in one week.
        try:
            url = self.fetch_code()
            code = self._parse_code(url)
            self.client.auth_with_code(code["code"])
            self.token = utils.JsonDict({"access_token": self.client.token_code, "expires_in": 7 * 24 * 60 * 60})
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None

    def is_expired(self, token=None):
        return False

    def auth(self):
        '''
        docstring placeholder
        '''
        try:
            if self.get_saved_token():
                self.client.auth_with_token(self.token["access_token"])
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

    @require_authed
    def home_timeline(self, count=20):
        try:
            jsonlist = self.client.miniblog.home_timeline(count)
        except Exception, e:
            logger.warning("DoubanAPIError, %s", e)
            return snstype.MessageList()
        statuslist = snstype.MessageList()
        for j in jsonlist:
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

    # Note:
    # The two following functions are solely for test purpose.
    # They should not be called during normal use.
    @require_authed
    def home_timeline_for_test(self, count=20):
        try:
            jsonlist = self.dummy()
        except Exception, e:
            logger.warning("DoubanAPIError, %s", e)
            return snstype.MessageList()
        statuslist = snstype.MessageList()
        for j in jsonlist:
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
    
    def dummy(self):
        return

    def update(self, text):
        try:
            self.client.miniblog.new(text)
            return True
        except Exception, e:
            logger.warning("DoubanAPIError: %s", e)
            return False

    @require_authed
    def reply(self, statusID, text):
        try:
            self.client.miniblog.comment.new(statusID.id, text)
            return True
        except Exception, e:
            logger.warning('DoubanAPIError: %s', str(e))
            return False

    @require_authed
    def like(self, message):
        try:
            self.client.miniblog.like(message.ID.id)
            return True
        except Exception, e:
            logger.warning("DoubanAPIError: %s", e)
            return False

    @require_authed
    def unlike(self, message):
        try:
            self.client.miniblog.unlike(message.ID.id)
            return True
        except Exception, e:
            logger.warning("DoubanAPIError, %s", e)
            return False
        
    @require_authed
    def forward(self, message, text):
        try:
            self.client.miniblog.reshare(message.ID.id)
            return True
        except Exception, e:
            logger.warning("DoubanAPIError: %s", e)
            return False

if __name__ == '__main__':

    sp = DoubanFeed.new_channel()
    sp['platform']="DoubanFeed"
    sp['app_key']="0c1f7169eb6ceb80245e543dc246c280"
    sp['app_secret']="d8ccd01506219118"
    sp["auth_info"]["callback_url"] = "http://snsapi.sinaapp.com/auth.php"
    renren = DoubanFeed(sp)
    renren.auth()
    sl = renren.home_timeline(20)
    renren.unlike(sl[1])
    renren.unlike(sl[0])