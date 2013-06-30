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
from snsapi import utils as snsapi_utils

sys.path = [DIR_TEST] + sys.path

class TestSNSAPIUtils(TestBase):
    #pass
#class TestTimeConversion(TestSNSAPIUtils):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_str2utc_normal(self):
        #TODO:
        #    More variants. Make sure the str date can be parsed.
        eq_(snsapi_utils.str2utc('Wed Jun 26 16:06:57 HKT 2013'), 1372234017)
        eq_(snsapi_utils.str2utc('Wed Jun 26 16:06:57 2013 HKT'), 1372234017)
        eq_(snsapi_utils.str2utc('Wed Jun 26 16:06:57 2013 +8:00'), 1372234017)
        eq_(snsapi_utils.str2utc('Wed Jun 26 16:06:57 2013 +08:00'), 1372234017)

    def test_str2utc_with_correction(self):
        # One sample time string returned by Renren
        # Test with Timezone Correction (TC):
        eq_(snsapi_utils.str2utc('2013-06-26 16:13:02', tc='+08:00'), 1372234382)
        # Test without Timezone Correction (TC): 8 hours late than correct time
        eq_(snsapi_utils.str2utc('2013-06-26 16:13:02'), 1372263182)

    def test_utc2str_normal(self):
        # We make the RFC822 compliant time string
        # Since the formatting depends on the TZ of current machine, 
        # we can only test the reflection between 'utc2str' and 'str2utc'
        eq_(snsapi_utils.str2utc(snsapi_utils.utc2str(1372234235)), 1372234235)
        eq_(snsapi_utils.str2utc(snsapi_utils.utc2str(1172234235)), 1172234235)
        #from dateutil import parser as dtparser, tz
        #eq_(snsapi_utils.utc2str(1372234235), 'Wed, 26 Jun 2013 16:10:35 HKT')
