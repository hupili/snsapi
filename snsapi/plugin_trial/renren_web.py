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
from xiaohuangji.renren import RenRen as RenrenXiaohuangjiInt

logger.debug("%s plugged!", __file__)

class RenrenWebError(Exception):
    def __init__(self, code, message):
        super(RenrenAPIError, self).__init__(message)
        self.code = code

class RenrenWebBase(RenrenXiaohuangjiInt):
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
        c['platform'] = 'RenrenWebBase'
        c['auth_info'] = {'save_token_file': '(default)', 
                          'cmd_request_url': '(dummy)', 
                          'callback_url': 'http://snsapi.sinaapp.com/auth.php', 
                          'cmd_fetch_code': '(dummy)',
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
        pass

    def auth_second(self):
        '''
        docstring placeholder
        '''
        pass

    def auth(self):
        '''
        docstring placeholder
        '''
        pass

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
    def home_timeline(self, count=20):
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
    renren = RenrenXiaohuangjiInt()
    renren.login(accounts[0][0], accounts[0][1])
    print renren.info

