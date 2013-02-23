#-*- encoding: utf-8 -*-

'''
Renren Web Interface 

Depends on xiaohuangji interfaces
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

from os.path import abspath, join, dirname
__DIR_ME = abspath(__file__)
__DIR_THIRD = join(dirname(dirname(__DIR_ME)), 'third')
sys.path.append(__DIR_THIRD)
from xiaohuangji.renren import RenRen as RenrenXiaohuangji
import requests

logger.debug("%s plugged!", __file__)

class RenrenWebError(Exception):
    def __init__(self, code, message):
        super(RenrenAPIError, self).__init__(message)
        self.code = code

class RenrenWebBase(SNSBase):
    def __init__(self, channel = None):
        super(RenrenWebBase, self).__init__(channel)
        self.platform = self.__class__.__name__
        self._renren = RenrenXiaohuangji()

        self._icode_fn = None

    def _cookie_str2jar(self, cookie_str):
        cookie_dict = dict([v.split('=', 1) for v in cookie_str.strip().split(';')])
        return requests.utils.cookiejar_from_dict(cookie_dict)

    def _cookie_jar2str(self, cookie_jar):
        cookie_dict = requests.utils.dict_from_cookiejar(cookie_jar)
        return ';'.join([k + '=' + v for k, v in cookie_dict.iteritems()])

    def _token_xiaohuangji2snsapi(self):
        obj = {'cookie': self._cookie_jar2str(self._renren.session.cookies),
               'token': self._renren.token,
               'info': self._renren.info}
        self.token = obj

    def _token_snsapi2xiaohuangji(self):
        obj = self.token
        self._renren.session.cookies = self._cookie_str2jar(obj['cookie'])
        self._renren.token = obj['token']
        self._renren.info = obj['info']
        self._renren.getToken()
        if self._renren.token['requestToken'] != '':
            return True
        else:
            return False

    @staticmethod
    def new_channel(full = False):
        '''
        docstring placeholder
        '''

        c = SNSBase.new_channel(full)

        c['app_key'] = ''
        c['app_secret'] = ''
        c['platform'] = 'RenrenWebBase'
        c['auth_info'] = {'save_token_file': '(default)', 
                          'cmd_request_url': '(console_output)', 
                          'callback_url': 'http://snsapi.sinaapp.com/auth.php', 
                          'cmd_fetch_code': '(console_input)',
                          'login_username': '',
                          'login_password': ''
                          } 

        return c
        
    def read_channel(self, channel):
        '''
        docstring placeholder
        '''

        super(RenrenWebBase, self).read_channel(channel) 

        # Renren API document says the limit is 140 character....
        # After test, it seems 245 unicode character. 
        # To leave some safe margin, we use 240 here. 
        self.jsonconf['text_length_limit'] = 240
        
    def need_auth(self):
        '''
        docstring placeholder
        '''

        return True
        
    def auth_first(self):
        '''
        docstring placeholder
        '''
        if self._renren.getShowCaptcha():
            import os
            self._icode_fn = 'icode.%s.jpg' % os.getpid()
            self._renren.getICode(self._icode_fn)
            logger.warning('This is renren_web API, mimicing auth flow. '
                    + 'Please input the captcha in this format: "http://me/?code={Your captcha here}"'
                    + 'We will improve this point later')
            self.request_url(self._icode_fn)
        else:
            logger.info('No captcha is needed. We will log in renren web automatically.')

    def auth_second(self):
        '''
        docstring placeholder
        '''
        url = self.fetch_code()
        params = self._parse_code(url)
        self._renren._login(self.jsonconf.auth_info['login_username'], 
                self.jsonconf.auth_info['login_password'], 
                params['code'])

        if self._icode_fn:
            import os
            os.remove(self._icode_fn)
            self._icode_fn = None

    def auth(self):
        '''
        docstring placeholder
        '''
        if self.get_saved_token() and self._token_snsapi2xiaohuangji():
            return

        logger.info("Try to authenticate '%s'", self.jsonconf.channel_name)
        self.auth_first()
        self.auth_second()
        self._token_xiaohuangji2snsapi()
        self.save_token()
        logger.debug("The token is" + str(self.token))
        logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)

    def expire_after(self, token = None):
        '''
        Calculate how long it is before token expire. 

        :return:

           * >0: the time in seconds. 
           * 0: has already expired. 
           * -1: there is no token expire issue for this platform. 
             (RenrenWeb series do not return this one)

        **NOTE:** The behaviour is different from that of SNSBase. 
        We omit one 'token' parameter for simplicity. That is, you 
        can only test the expiration time the current instance is 
        holding but not other arbitrary tokens. If 'token' is not 
        None, we just pretend it has expired. 

        '''
        if not token is None:
            return 0
        try:
            if self._token_snsapi2xiaohuangji():
                # Any positive number can do
                return 1
            else: 
                # Current token is invalid, need to re auth()
                return 0
        except Exception, e:
            logger.warning('Catch exception: %s', e)
            return 0

class RenrenWebNotificationMessage(snstype.Message):
    platform = "RenrenWebNotification"

    def parse(self):
        self.ID.platform = self.platform
        self._parse_notification(self.raw)

    def _parse_notification(self, dct):
        # Below is old logic for reference
        self.ID.status_id = dct["source_id"]
        self.ID.source_user_id = dct["actor_id"]

        self.parsed.userid = dct['actor_id']
        self.parsed.username = dct['name']
        self.parsed.time = utils.str2utc(dct["update_time"], " +08:00")

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


class RenrenWebNotification(RenrenWebBase):

    Message = RenrenWebNotificationMessage

    def __init__(self, channel = None):
        super(RenrenShare, self).__init__(channel)
        self.platform = self.__class__.__name__

    @staticmethod
    def new_channel(full = False):
        '''
        docstring placeholder

        '''

        c = RenrenWebBase.new_channel(full)
        c['platform'] = 'RenrenWebNotification'
        return c
        
    @require_authed
    def home_timeline(self, count=1):
        '''
        Get timeline of Renren statuses

        :param count: 
            Number of statuses

        :return:
            At most ``count`` statuses (can be less).
        '''

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
    def reply(self, mID, text):
        '''
        docstring placeholder
        '''

        try:
            # Do sth.
            logger.debug("Reply to status '%s' return: %s", mID, ret)
            # Do sth. equivalent
            if 'result' in ret and ret['result'] == 1:
                logger.info("Reply '%s' to status '%s' succeed", text, mID)
                return True
            else:
                return False
        except Exception, e:
            logger.warning("Reply failed: %s", e)

        logger.info("Reply '%s' to status '%s' fail", text, mID)
        return False

if __name__ == '__main__':
    try:
        from my_accounts import accounts
    except:
        print "please configure your renren account in 'my_account.py' first"
        sys.exit(-1)

    nc = RenrenWebBase.new_channel()
    nc['auth_info']['login_username'] = accounts[0][0]
    nc['auth_info']['login_password'] = accounts[0][1]

    print nc

    renren = RenrenWebBase(nc)
    renren.auth()
    print renren._renren.getUserInfo()

    #renren = RenrenXiaohuangjiInt()
    #renren.login(accounts[0][0], accounts[0][1])
    #notifications = renren.getNotifications()
    #print notifications
    #for n in notifications:
    #    payloads, content = renren.getNotiData(n)
    #    print payloads
    #    print content
    #    payloads['message'] = 'test reply "%s"' % content
