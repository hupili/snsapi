# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

from snsconf import SNSConf

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

class JsonDict(JsonObject):
    """
    The wrapper class for Python dict. 

    It is intended to host Json compatible objects. 
    In the interative CLI, the users are expected 
    to configure SNSAPI during execution. To present
    the current config in a nice way. We should add
    indentation for the dump method.
    """
    def __init__(self, jsonconf = None):
        super(JsonDict, self).__init__()
        if jsonconf:
            self.update(jsonconf)

    def __str__(self):
        return self._dumps_pretty()

    def _dumps(self):
        return json.dumps(self)

    def _dumps_pretty(self):
        return json.dumps(self, indent=2)

    def get(self, attr):
        '''
        dict entry reading with fault tolerance. 

        e.g. RSS format is very diverse. 
        To my current knowledge, some formats have 'author' fields, 
        but others do not:
           * rss : no
           * rss2 : yes
           * atom : yes
           * rdf : yes
        This function will return a string "(null)" by default if the 
        field does not exist. The purpose is to expose unified interface
        to upper layers. (seeing "(null)" is better than catching an error. 

        '''
        return dict.get(self, attr, "(null)")

        
def console_input(string = None):
    '''
    To make oauth2 testable, and more reusable, we use console_input to wrap raw_input.
    See http://stackoverflow.com/questions/2617057/supply-inputs-to-python-unittests.
    '''
    if string is None:
        return raw_input().decode(SNSConf.SNSAPI_CONSOLE_STDIN_ENCODING)
    else:
        return string.decode(SNSConf.SNSAPI_CONSOLE_STDIN_ENCODING)

def console_output(string):
    '''
    The sister function of console_input()!

    Actually it has a much longer story. See Issue#8: 
    the discussion of console encoding~
    '''
    print string.encode(SNSConf.SNSAPI_CONSOLE_STDOUT_ENCODING)

#TODO:
#    Find simpler implementation for str2utc() and utc2str()
#    The current implementation JUST WORKS. It is far from 
#    satisfactory. I surveyed the Internet but found no "correct"
#    solution. Many of those implementations on the Internet 
#    only work with local time. 
#
#    What I want is simple:
#       * Convert between unix timestamp (integer) and 
#       an RFC822 string. 
#       * The string SHOULD CONTAIN time zone either in 
#       text or number format. It is parse-able. Using local 
#       time zone is favoured but not mandatory. 
import calendar
import time
import datetime
from dateutil import parser as dtparser, tz
from third.PyRSS2Gen import _format_date

def str2utc(s):
    d = dtparser.parse(s)
    #print d 
    #print d.utctimetuple()
    return calendar.timegm(d.utctimetuple())

def utc2str(u):
    #return str(datetime.datetime.fromtimestamp(u))
    #return _format_date(datetime.datetime.utcfromtimestamp(u))
    return _format_date(datetime.datetime.fromtimestamp(u, tz.tzlocal()))
    
if __name__ == '__main__':
    u = time.time()
    print u
    s = utc2str(u)
    print s
    print str2utc(s)
