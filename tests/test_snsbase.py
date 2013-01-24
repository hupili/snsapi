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

