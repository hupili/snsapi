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
from snsapi.plugin_trial import renren

sys.path = [DIR_TEST] + sys.path

class TestRenrenStatus(TestBase):

    def setup(self):
        self.channel = renren.RenrenStatus(get_data('email-channel-conf.json.test'))

    def teardown(self):
        self.channel = None
        pass

    def test_renren_init(self):
        eq_(self.channel.platform, "RenrenStatus")

    def test_renren_new_channel_normal(self):
        nc = renren.RenrenStatus.new_channel()
        in_('channel_name', nc)
        in_('open', nc)
        in_('platform', nc)

    def _fake_authed(self, authed=True):
        self.channel.is_authed = lambda *args, **kwargs: authed

    def _fake_http_json_api_response(self, response):
        self.channel.renren_request = lambda *args, **kwargs: response

    def test_renren_home_timeline_normal(self):
        pass

    def test_renren_home_timeline_abnormal(self):
        # feed type=10 should not return this data structure.
        # There was no such structure when we initiated snsapi.
        # The bug was found on June 22, 2013.
        # 'renren-feed-status-2.json.test' contains such a case.
        # We have to make the message parse more robust.
        self._fake_authed()
        self._fake_http_json_api_response(get_data('renren-feed-status-2.json.test'))
        ht = self.channel.home_timeline()
        eq_(len(ht), 1)
        eq_(ht[0].parsed['text'], 'message "title" ')
        eq_(ht[0].parsed['username'], 'user5')
        eq_(ht[0].parsed['userid'], '6666')

