# -*- coding: utf-8 -*-

__author__ = 'hupili'
__copyright__ = 'Unlicensed'
__license__ = 'Unlicensed'
__version__ = '0.1'
__maintainer__ = 'hupili'
__email__ = 'hpl1989@gmail.com'
__status__ = 'development'

from nose.tools import ok_
from nose.tools import eq_
from test_config import *
from test_utils import *

from snsapi import snstype
from snsapi.plugin import rss

sys.path = [DIR_TEST] + sys.path

class TestRSS(TestBase):

    def setup(self):
        pass

    def teardown(self):
        pass

class TestRSSSummary(TestBase):

    def setup(self):
        pass

    def teardown(self):
        pass

class TestRSS2RW(TestBase):

    def setup(self):
        channel_conf = {
          "url": "_test_rss.xml", 
          "channel_name": "test_rss", 
          "open": "yes", 
          "platform": "RSS2RW"
        }
        self.rss = rss.RSS2RW(channel_conf)

    def teardown(self):
        _url = self.rss.jsonconf.url
        import os
        if os.path.isfile(_url):
            os.unlink(_url)
        del self.rss

    def test_rss2rw_update_text(self):
        import time
        _time1 = int(time.time())
        # Execution takes time
        self.rss.update('test status')
        _time2 = int(time.time())
        msg = self.rss.home_timeline()[0]
        ok_(msg.parsed.time >= _time1 and msg.parsed.time <= _time2)
        eq_(msg.parsed.text, 'test status')
        # The default settings
        eq_(msg.parsed.username, 'snsapi')
        eq_(msg.parsed.userid, 'snsapi')

    def test_rss2rw_update_text_with_author(self):
        self.rss.jsonconf.author = 'test_author'
        import time
        _time1 = int(time.time())
        # Execution takes time
        self.rss.update('test status')
        _time2 = int(time.time())
        msg = self.rss.home_timeline()[0]
        ok_(msg.parsed.time >= _time1 and msg.parsed.time <= _time2)
        eq_(msg.parsed.text, 'test status')
        # The default settings
        eq_(msg.parsed.username, 'test_author')
        eq_(msg.parsed.userid, 'test_author')

    def test_rss2rw_update_message(self):
        import time
        # Use the generic Message instead of RSS2RW.Message
        msg = snstype.Message()
        msg.parsed.username = "test_username"
        msg.parsed.userid = "test_userid"
        msg.parsed.time = int(time.time())
        msg.parsed.text = "test status"
        self.rss.update(msg)
        msg2 = self.rss.home_timeline()[0]
        eq_(msg.parsed.time, msg2.parsed.time)
        eq_(msg.parsed.username, msg2.parsed.username)
        eq_(msg.parsed.userid, msg2.parsed.userid)
        eq_(msg.parsed.text, msg2.parsed.text)

