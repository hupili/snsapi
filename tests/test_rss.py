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
        _url = os.path.join(DIR_TMP, "_test_rss.xml")
        channel_conf = {
          "url": _url,
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

    def test_rss2rw_update_text_str(self):
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

    def test_rss2rw_update_text_unicode(self):
        import time
        _time1 = int(time.time())
        # Execution takes time
        self.rss.update(u'test status unicode')
        _time2 = int(time.time())
        msg = self.rss.home_timeline()[0]
        ok_(msg.parsed.time >= _time1 and msg.parsed.time <= _time2)
        eq_(msg.parsed.text, 'test status unicode')
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
        # Current RSS feeds do not distinguish userid and username
        # In the future, userid may be coded into our special structure
        msg.parsed.userid = "test_username"
        msg.parsed.time = int(time.time())
        msg.parsed.text = "test status"
        self.rss.update(msg)
        msg2 = self.rss.home_timeline()[0]
        eq_(msg.parsed.time, msg2.parsed.time)
        eq_(msg.parsed.username, msg2.parsed.username)
        eq_(msg.parsed.userid, msg2.parsed.userid)
        eq_(msg.parsed.text, msg2.parsed.text)

    def test_rss2rw_update_message_timeout_append(self):
        # We can not make the RSS feed go arbitrary long.
        # Timeout-ed entried will be deleted upon every update operation.
        # This UT tests the behaviour when appending a timeout-ed item.
        import time
        _cur_time = int(time.time())
        # Use the generic Message instead of RSS2RW.Message
        msg = snstype.Message()
        msg.parsed.username = "test_username"
        msg.parsed.userid = "test_username"
        msg.parsed.time = _cur_time
        msg.parsed.text = "test status"

        self.rss.update(msg)
        self.rss.update(msg)
        eq_(len(self.rss.home_timeline()), 2)

        self.rss.update(msg)
        eq_(len(self.rss.home_timeline()), 3)

        # 1 second before timeout
        msg.parsed.time -= self.rss.jsonconf.entry_timeout - 1
        self.rss.update(msg)
        eq_(len(self.rss.home_timeline()), 4)

        # 1 second after timeout
        # Should reject this entry
        msg.parsed.time -= 2
        self.rss.update(msg)
        eq_(len(self.rss.home_timeline()), 4)

    def test_rss2rw_update_message_timeout_simulate(self):
        # This UT simulates a timeout scenario
        import time
        _cur_time = int(time.time())
        # Use the generic Message instead of RSS2RW.Message
        msg = snstype.Message()
        msg.parsed.username = "test_username"
        msg.parsed.userid = "test_username"
        msg.parsed.time = _cur_time
        msg.parsed.text = "test status"

        # Normal update
        self.rss.update(msg)
        eq_(len(self.rss.home_timeline()), 1)

        # Change our timer
        _new_time = _cur_time + self.rss.jsonconf.entry_timeout + 1
        time.time = lambda : _new_time
        msg.parsed.time = int(time.time())
        self.rss.update(msg)
        # The previous message is kicked out
        eq_(len(self.rss.home_timeline()), 1)

    def test_rss2rw_update_message_make_link(self):
        # Check the link is correctly generated
        # See ``_make_link`` for more info.
        # None: no timeout; keep all entries permanently
        self.rss.jsonconf.entry_timeout = None
        msg = snstype.Message()
        msg.parsed.username = "test_username"
        msg.parsed.userid = "test_username"
        msg.parsed.text = "test status"
        msg.parsed.time = 1234567890
        self.rss.update(msg)
        msg2 = self.rss.home_timeline()[0]
        eq_(msg2.parsed.link, 'http://goo.gl/7aokV#a6dd6e622b2b4f01065b6abe47571a33423a16ea')
