# -*- coding: utf-8 -*-

__author__ = 'hupili'
__copyright__ = 'Unlicensed'
__license__ = 'Unlicensed'
__version__ = '0.1'
__maintainer__ = 'hupili'
__email__ = 'hpl1989@gmail.com'
__status__ = 'development'

from test_config import *
from test_utils import *
from snsapi.plugin_trial import renren

sys.path = [DIR_TEST] + sys.path

class TestRenrenFeed(TestBase):

    def setup(self):
        self.channel = renren.RenrenFeed(get_data('renren-channel-conf.json.test'))

    def teardown(self):
        self.channel = None
        pass

    def test_renren_init(self):
        eq_(self.channel.platform, "RenrenFeed")

    def test_renren_new_channel_normal(self):
        nc = renren.RenrenFeed.new_channel()
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
        print(str(ht[0].parsed))
        eq_(ht[0].parsed['text'], 'nice "good" http://photo.renren.com/photo/544815307/album')
        eq_(ht[0].parsed['username'], 'wcyz666')
        eq_(ht[0].parsed['userid'], '544815307')
        eq_(ht[0].parsed['feed_type'], 'PUBLISH_ONE_PHOTO')

    def renren_request_return_api_error(self, **kwargs):
        raise renren.RenrenAPIError(9999999, 'this is a fake error')

    def test_renren_status_update(self):
        self._fake_authed()
        self.channel.renren_request = self.renren_request_return_api_error
        eq_(self.channel.update('test status'), False)
