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
        pass

    def teardown(self):
        pass

    def test_snsbase_new_channel_normal(self):
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

