#-*-coding:utf-8-*-

"""
Nosetest configs 
"""

from nose.tools import ok_
from test_config import NO_SUCH_KEY_ERROR_TEMPLATE
from test_config import DIR_TEST_DATA
from test_config import WRONG_RESULT_ERROR
import json
import os.path

def in_(k, dct):
    '''
    Helper function to assert a key is in a dict. The naming
    is following nose's format. 

    :param k: Key 
    :type k: str
    :param dct: Dict
    :type dct: dict

    '''
    ok_((k in dct), NO_SUCH_KEY_ERROR_TEMPLATE % (k))

def gt_(a, b):
    '''
    Helper function to assert ``a`` is greater than ``b``

    :type a,b: Any comparable type

    '''
    ok_((a > b), WRONG_RESULT_ERROR)

def nok_(v):
    '''
    Helper function to assert Not-OK (NOK)

    :type v: Boolean

    '''
    ok_(not v)

def get_data(filename):
    return json.load(open(os.path.join(DIR_TEST_DATA, filename), 'r'))
