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
        self.channel = douban.DoubanFeed(get_data('Douban-channel-conf.json.test'))

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

    def _fake_authed(self, authed=True):
        self.channel.is_authed = lambda *args, **kwargs: authed

    def _fake_http_json_api_response(self, response):
        self.channel.douban_request = lambda *args, **kwargs: response

    def test_Douban_home_timeline_normal(self):
        self._fake_authed()
        self._fake_http_json_api_response(get_data('Douban-feed-status-2.json.test'))
        ht = self.channel.home_timeline()
        eq_(len(ht), 1)
        eq_(ht[0].parsed['text'], 'Taken on the coach to Edinburgh... Amazing:) #blue #scotland')
        eq_(ht[0].parsed['username'], 'zoealviz')
        eq_(ht[0].parsed['userid'], '388063006')
        eq_(ht[0].parsed['attachments'][0]['data'], 'http://scontent-a.cdndouban.com/hphotos-xpf1/t51.2885-15/10513922_1487869904784115_1918043968_n.jpg')
        eq_(ht[0].parsed['attachments'][0]['type'], 'picture')
        eq_(ht[0].parsed['attachments'][0]['format'][0], 'link')

    def Douban_request_return_api_error(self, **kwargs):
        raise douban.DoubanAPIError(9999999, 'this is a fake error')