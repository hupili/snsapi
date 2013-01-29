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
from snsapi.plugin_trial.emails import Email

sys.path = [DIR_TEST] + sys.path

class TestSNSBase(TestBase):

    def setup(self):
        self.channel = Email(get_data('email-channel-conf.json.test'))
        pass

    def teardown(self):
        self.channel = None
        pass

    def _fake_authed(self):
        self.channel.imap_ok = True
        self.channel.smtp_ok = True

    def test_email_init(self):
        eq_(self.channel.platform, "Email")
        eq_(self.channel.imap, None)
        eq_(self.channel.imap_ok, False)
        eq_(self.channel.smtp, None)
        eq_(self.channel.smtp_ok, False)

    def test_email_new_channel_normal(self):
        nc = Email.new_channel()
        in_('address', nc)
        in_('channel_name', nc)
        in_('imap_host', nc)
        in_('imap_port', nc)
        in_('open', nc)
        in_('password', nc)
        in_('platform', nc)
        in_('smtp_host', nc)
        in_('smtp_port', nc)
        in_('username', nc)

    def test_email_home_timeline_normal(self):
        self._fake_authed()
        self.channel._receive = lambda *al, **ad: get_data('email-_receive.json.test')
        sl = self.channel.home_timeline(1)
        eq_(len(sl), 1)
        # Check common Message fields
        ok_(isinstance(sl[0], snstype.Message))
        in_('username', sl[0].parsed)
        in_('userid', sl[0].parsed)
        in_('time', sl[0].parsed)
        in_('text', sl[0].parsed)
        ok_(isinstance(sl[0].parsed['time'], int))
        # Check email spcific fields
        in_('title', sl[0].parsed)

    def test_email_home_timeline_not_authed(self):
        # All plugin public interfaces do not raise error.
        # Return 'None' when the platform has not been authed. 
        eq_(self.channel.home_timeline(), None)

    def _timeline_with_malformed_email_raw_data(self, field, value):
        d = get_data('email-_receive.json.test')[0]
        d[field] = value
        self.channel._receive = lambda *al, **ad: [d]
        return self.channel.home_timeline(1)

    def test_email_home_timeline_empty(self):
        # All plugin public interfaces do not raise error.
        # Return [] if no messages can be parsed. 
        self._fake_authed()
        # Can not parse: return []
        eq_(self._timeline_with_malformed_email_raw_data('Date', None), [])
        # Irrelevant field: normally return one Message
        eq_(len(self._timeline_with_malformed_email_raw_data('_irrelevant', None)), 1)
