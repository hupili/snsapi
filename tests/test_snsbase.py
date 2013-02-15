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
from snsapi.snsbase import SNSBase

sys.path = [DIR_TEST] + sys.path

class TestSNSBase(TestBase):

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_snsbase_new_channel_normal(self):
        nc = SNSBase.new_channel()
        eq_(2, len(nc), WRONG_RESULT_ERROR)
        in_('channel_name', nc)
        in_('open', nc)

    def test_snsbase_new_channel_full(self):
        nc = SNSBase.new_channel(full=True)
        eq_(4, len(nc), WRONG_RESULT_ERROR)
        in_('channel_name', nc)
        in_('open', nc)
        in_('description', nc)
        in_('methods', nc)

    def _parse_code_ok(self, url, code):
        sns = SNSBase()
        token = sns._parse_code(url)
        ok_(isinstance(token, snsapi.utils.JsonDict))
        eq_(token.code, code)

    def test__parse_code(self):
        # Sina example
        self._parse_code_ok('http://copy.the.code.to.client/?code=b5ffaed78a284a55e81ffe142c4771d9', 'b5ffaed78a284a55e81ffe142c4771d9')
        # Tencent example
        self._parse_code_ok('http://copy.the.code.to.client/?code=fad92807419b5aac433c4128A05e1Cad&openid=921CFC3AF04d76FE59D98a2029D0B978&openkey=6C2FCABD153B18625BAAB1BA206EF2C6', 'fad92807419b5aac433c4128A05e1Cad')
