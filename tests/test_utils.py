#-*-coding:utf-8-*-

"""
Nosetest configs 
"""

from nose.tools import ok_
from test_config import NO_SUCH_KEY_ERROR_TEMPLATE
from test_config import DIR_TEST_DATA
import json
import os.path

def in_(k, dct):
    '''
    Helper function to assert a key is in a dict. The naming
    is following nose's format. 

    :k:
        str, Key 
    :dct:
        dict
    '''
    ok_((k in dct), NO_SUCH_KEY_ERROR_TEMPLATE % (k))

def get_data(filename):
    return json.load(open(os.path.join(DIR_TEST_DATA, filename), 'r'))
