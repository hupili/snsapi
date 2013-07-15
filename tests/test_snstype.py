from nose.tools import ok_
from nose.tools import eq_
from test_config import *
from test_utils import *

import snsapi
from snsapi.snstype import BooleanWrappedData

sys.path = [DIR_TEST] + sys.path

class TestSNSType(TestBase):

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_snstype_boolean_wrapped(self):
        false_wrapped = BooleanWrappedData(False)
        true_wrapped = BooleanWrappedData(True)
        ok_(true_wrapped == True)
        ok_(true_wrapped != False)
        ok_(false_wrapped == False)
        ok_(false_wrapped != True)
        ok_(true_wrapped)
        ok_(not false_wrapped)
