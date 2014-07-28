# -*- coding: utf-8 -*-

__author__ = 'wcyz666'
__copyright__ = 'Unlicensed'
__license__ = 'Unlicensed'
__version__ = '0.1'
__maintainer__ = 'wcyz666'
__email__ = 'wcyz666@126.com'
__status__ = 'development'

from test_config import *
from test_utils import *
from snsapi.plugin_trial import douban


sys.path = [DIR_TEST] + sys.path

class TestDoubanFeed(TestBase):

    def setup(self):
        self.channel = douban.DoubanFeed(get_data('douban-channel-conf.json.test'))

    def teardown(self):
        self.channel = None
        pass

    def test_Douban_init(self):
        eq_(self.channel.platform, "DoubanFeed")

    def test_Douban_new_channel_normal(self):
        nc = douban.DoubanFeed.new_channel()
        in_('channel_name', nc)
        in_('open', nc)
        in_('platform', nc)

    def _fake_timeline(self):
        return get_data('douban-feed-status-2.json.test')

    def _fake_auth(self):
        return

    def _fake_authed(self, authed=True):
        self.channel.is_authed = lambda *args, **kwargs: authed

    def _fake_http_json_api_response(self):
        self.channel.dummy = self._fake_timeline
        self.channel.auth = self._fake_auth
        self.channel.auth()

    def test_Douban_home_timeline_normal(self):
        self._fake_authed()
        self._fake_http_json_api_response()
        ht = self.channel.home_timeline_for_test()
        eq_(len(ht), 1)
        eq_(ht[0].parsed['username'], 'wcyz666')
        eq_(ht[0].parsed['userid'], '93836298')
        eq_(ht[0].parsed['attachments'][0]['data'], 'http://img3.douban.com/view/status/raw/public/2758c76c154c0af.jpg')
        eq_(ht[0].parsed['attachments'][0]['type'], 'picture')
        eq_(ht[0].parsed['attachments'][0]['format'][0], 'link')

    def Douban_request_return_api_error(self, **kwargs):
        raise douban.DoubanAPIError(9999999, 'this is a fake error')

if __name__ == '__main__':
    test = TestDoubanFeed()
    test.setup()
    test.test_Douban_init()
    test.test_Douban_new_channel_normal()
    test.test_Douban_home_timeline_normal()
    test.Douban_request_return_api_error()