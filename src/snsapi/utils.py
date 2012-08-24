# -*- coding: utf-8 -*-

import snsconf

'''
utilities for snsapi
'''

class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
        
#TODO: 
#The name of this function is non-informative
#Probably change it to another one later
def _obj_hook(pairs):
    '''
    convert json object to python object.
    '''
    o = JsonObject()
    for k, v in pairs.iteritems():
        o[str(k)] = v
    return o

def console_input():
    '''
    To make oauth2 testable, and more reusable, we use console_input to wrap raw_input.
    See http://stackoverflow.com/questions/2617057/supply-inputs-to-python-unittests.
    '''
    return raw_input()

def console_output(string):
    '''
    The sister function of console_intput()!

    Actually it has a much longer story. See Issue#8: 
    the discussion of console encoding~
    '''
    print string.encode(snsconf.SNSAPI_CONSOLE_STDOUT_ENCODING)

