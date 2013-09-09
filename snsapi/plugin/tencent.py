#-*- encoding: utf-8 -*-

'''
Tencent Weibo Client
'''

from ..snslog import SNSLog as logger
from ..snsbase import SNSBase, require_authed
from .. import snstype
from .. import utils

logger.debug("%s plugged!", __file__)

class TencentWeiboStatusMessage(snstype.Message):
    platform = "TencentWeiboStatus"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        #TODO: unify the data type
        #      In SinaAPI, 'created_at' is a string
        #      In TecentWeibo, 'created_at' is an int
        #Proposal:
        #      1. Store a copy of dct object in the Status object.
        #         Derived class of TecentWeibo or SinaAPI can extract
        #         other fields for future use.
        #      2. Defaultly convert every fields into unicode string.
        #         Upper layer can tackle with a unified interface

        self.ID.reid = dct['id']

        self.parsed.time = dct['timestamp']
        self.parsed.userid = dct['name']
        self.parsed.username = dct['nick']

        # The 'origtext' field is plaintext.
        # URLs in 'text' field is parsed to HTML tag
        self.parsed.reposts_count = dct['count']
        self.parsed.comments_count = dct['mcount']
        self.parsed.text_last = utils.html_entity_unescape(dct['origtext'])
        if 'source' in dct and dct['source']:
            self.parsed.text_trace = utils.html_entity_unescape(dct['origtext'])
            self.parsed.text_orig = utils.html_entity_unescape(dct['source']['origtext'])
            self.parsed.username_orig = utils.html_entity_unescape(dct['source']['nick'])
            self.parsed.text = self.parsed.text_trace \
                    + " || " + "@" + self.parsed.username_orig \
                    + " : " + self.parsed.text_orig
        else:
            self.parsed.text_trace = None
            self.parsed.text_orig = utils.html_entity_unescape(dct['origtext'])
            self.parsed.username_orig = dct['nick']
            self.parsed.text = utils.html_entity_unescape(dct['origtext'])

        #TODO:
        #    retire past fields
        #self.ID.reid = dct['id']
        #self.parsed.id = dct['id']
        #self.parsed.created_at = dct['timestamp']
        #self.parsed.text = dct['text']
        #self.parsed.reposts_count = dct['count']
        #self.parsed.comments_count = dct['mcount']
        #self.parsed.username = dct['name']
        #self.parsed.usernick = dct['nick']

class TencentWeiboStatus(SNSBase):

    Message = TencentWeiboStatusMessage

    def __init__(self, channel = None):
        super(TencentWeiboStatus, self).__init__(channel)

        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['app_key'] = ''
        c['app_secret'] = ''
        c['platform'] = 'TencentWeiboStatus'
        c['auth_info'] = {
                "save_token_file": "(default)",
                "cmd_request_url": "(default)",
                "callback_url": "http://snsapi.sinaapp.com/auth.php",
                "cmd_fetch_code": "(default)"
                }

        return c

    def read_channel(self, channel):
        super(TencentWeiboStatus, self).read_channel(channel)

        if not "auth_url" in self.auth_info:
            self.auth_info.auth_url = "https://open.t.qq.com/cgi-bin/oauth2/"
        if not "callback_url" in self.auth_info:
            self.auth_info.callback_url = "http://snsapi.sinaapp.com/auth.php"

        # Tencent limit is a little more than 140.
        # We just use 140, which is a global industrial standard.
        self.jsonconf['text_length_limit'] = 140

        #if not 'platform_prefix' in self.jsonconf:
        #    self.jsonconf['platform_prefix'] = u'腾讯'

    def need_auth(self):
        return True

    def auth_first(self):
        self._oauth2_first()

    def auth_second(self):
        try:
            self._oauth2_second()
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", e)
            self.token = None

    def _attach_authinfo(self, params):
        params['access_token'] = self.token.access_token
        params['openid'] = self.token.openid
        params['oauth_consumer_key'] = self.jsonconf.app_key
        params['oauth_version'] = '2.a'
        params['scope'] = 'all'
        return params

    def tencent_request(self, method, http_method="GET", files={}, **kwargs):
        self._attach_authinfo(kwargs)
        if http_method == "GET":
            return self._http_get("https://open.t.qq.com/api/" + method, params=kwargs)
        else:
            return self._http_post("https://open.t.qq.com/api/" + method, params=kwargs, files=files)

    @require_authed
    def home_timeline(self, count=20):
        '''Get home timeline

           * function : get statuses of yours and your friends'
           * parameter count: number of statuses
        '''

        jsonobj = self.tencent_request("statuses/home_timeline", reqnum=count)
        #logger.debug("returned: %s", jsonobj)

        statuslist = snstype.MessageList()
        try:
            for j in jsonobj['data']['info']:
                statuslist.append(self.Message(j,\
                    platform = self.jsonconf['platform'],\
                    channel = self.jsonconf['channel_name']\
                    ))
        except Exception, e:
            logger.warning("Catch exception: %s", e)
            return []
        return statuslist

    @require_authed
    def update(self, text, pic=None):
        '''update a status

           * parameter text: the update message
           * return: success or not
        '''

        text = self._cat(self.jsonconf['text_length_limit'], [(text,1)])

        if not pic:
            method = "t/add"
        else:
            method = "t/add_pic"

        try:
            if pic:
                ret = self.tencent_request(method, "POST", content=text, files={'pic': ('pic.jpg', pic)})
            else:
                ret = self.tencent_request(method, "POST", content=text)
            if(ret['msg'] == "ok"):
                logger.info("Update status '%s' on '%s' succeed", text, self.jsonconf.channel_name)
                return True
            else:
                return ret
        except Exception, e:
            logger.warning("Catch Exception: %s", e)
            return False

    @require_authed
    def reply(self, statusID, text):
        '''reply to a status

           * parameter text: the comment text
           * return: success or not
        '''
        ret = self.tencent_request("t/reply", "POST", content=text, reid=statusID.reid)
        if(ret['msg'] == "ok"):
            return True
        logger.info("Reply '%s' to status '%s' fail: %s", text, self.jsonconf.channel_name, ret)
        return ret

