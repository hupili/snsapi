# -*- coding: utf-8 -*-

import base64

try:
    import json
except ImportError:
    import simplejson as json

from snsconf import SNSConf
from snslog import SNSLog as logger
import multiprocessing

'''
utilities for snsapi
'''

class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        '''
        HU Pili 20121029:
            We modify the raised error type so that this object
            is pickle-serializable.

        See reference:
            http://bytes.com/topic/python/answers/626288-pickling-class-__getattr__
        '''
        try:
            return self[attr]
        except KeyError:
            raise AttributeError

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

    def get(self, attr, default_value = None):
        '''
        dict entry reading with fault tolerance.

        :attr:
            A str or a list of str.

        :return:
            The value corresponding to the (first) key, or default val.

        If attr is a list, we will try all the candidates until
        one 'get' is successful. If none of the candidates succeed,
        return a the ``default_value``.

        e.g. RSS format is very diverse.
        To my current knowledge, some formats have 'author' fields,
        but others do not:

           * rss : no
           * rss2 : yes
           * atom : yes
           * rdf : yes

        NOTE:

           * The original ``default_value`` is "(null)". Now we change
           to ``None``. ``None`` is more standard in Python and it does
           not have problem to convert to ``str`` (the usual way of
           using our data fields). It has the JSON counterpart: ``null``.

        '''
        #TODO:
        #    Check if other parts are broken due to this change from
        #    "(null)" to None.
        if isinstance(attr, str):
            return dict.get(self, attr, default_value)
        elif isinstance(attr, list):
            for a in attr:
                val = dict.get(self, a, None)
                if val:
                    return val
            return default_value
        else:
            logger.warning("Unkown type: %s", type(attr))
            return default_value


def obj2str(obj):
    '''
    Convert Python object to string using SNSApi convention.

    :param obj:
        A Python object that is "serializable".
        Check ``Serialize`` to what backend we use for serialization.
    '''
    return base64.encodestring(Serialize.dumps(obj))

def str2obj(string):
    '''
    Convert string to Python object using SNSApi convention.

    :param obj:
        A string constructed by ``obj2str``.
        Do not call this method on a string coming from an unkown source.
    '''
    return Serialize.loads(base64.decodestring(string))


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
from datetime import tzinfo, timedelta, datetime
from dateutil import parser as dtparser, tz
from third.PyRSS2Gen import _format_date

ZERO = timedelta(0)

class FixedOffsetTimeZone(tzinfo):
    """
    Fixed offset in minutes east from UTC.

    See ``third/timezone_sample.py`` for more samples.

    """
    def __init__(self, offset, name):
        '''
        Build a fixed offset ``tzinfo`` object.  No DST support.

        :type offset: int
        :param offset:
            Offset of your timezone in **MINUTES**
        :type name: str
        :param name:
            The name string of your timezone
        '''
        self.__offset = timedelta(minutes = offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

SNSAPI_TIMEZONE = FixedOffsetTimeZone(0, 'GMT')

try:
    SNSAPI_TIMEZONE = tz.tzlocal()
    logger.debug("Get local timezone OK. Use system's tzlocal")
except Exception as e:
    # Silently ignore it and degrades to default TZ (GMT).
    # Logger has not been set at the moment.
    #
    # In case other methods refer to tzlocal(),
    # we fix it by the default TZ configured here.
    # (The ``dtparser`` will refer to ``tz.tzlocal``)
    logger.warning("Get local timezone failed. Use default GMT")
    tz.tzlocal = lambda : SNSAPI_TIMEZONE

def str2utc(s, tc = None):
    '''
    :param tc:
        Timezone Correction (TC). A timezone suffix string.
        e.g. ``" +08:00"``, `` HKT``, etc.
        Some platforms are know to return time string without TZ
        (e.g. Renren). Manually do the correction.
    '''
    if tc and tc.strip() != '':
        s += tc

    try:
        d = dtparser.parse(s)
        #print d
        #print d.utctimetuple()
        return calendar.timegm(d.utctimetuple())
    except Exception, e:
        logger.warning("error parsing time str '%s': %s", s, e)
        return 0

def utc2str(u, tz=None):
    # Format to RFC822 time string in current timezone
    if tz is None:
        tz = SNSAPI_TIMEZONE
    return _format_date(datetime.fromtimestamp(u, tz))

import re
_PATTERN_HTML_TAG = re.compile('<[^<]+?>')
def strip_html(text):
    # Ref:
    #    * http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    return re.sub(_PATTERN_HTML_TAG, '', text)

import pickle

class Serialize(object):
    """
    The common serialization SAP

    """
    def __init__(self, *al, **ad):
        raise Exception("Use static methods of Serialize directly!")

    @staticmethod
    def loads(string):
        return pickle.loads(string)

    @staticmethod
    def dumps(obj):
        return pickle.dumps(obj)

import HTMLParser
def html_entity_unescape(s):
    '''
    Escape HTML entities, such as "&pound;"
    This interface always returns unicode no matter the input 's'
    is str or unicode.

    '''
    return HTMLParser.HTMLParser().unescape(s)

def report_time(func):
    def report_time_wrapper(*al, **ad):
        start = time.time()
        ret = func(*al, **ad)
        end = time.time()
        logger.info("Function '%s' execution time: %.2f", func.__name__, end - start)
        return ret
    return report_time_wrapper

@report_time
def _test_report_time(i):
    print "your number: %d" % i


class TimeoutException(Exception):
    pass

class RunnableProcess(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func, ) + args
        multiprocessing.Process.__init__(self, target=self.execute_func, args=args, kwargs=kwargs)

    def execute_func(self, func, *args, **kwargs):
        try:
            r = func(*args, **kwargs)
            self.queue.put((True, r))
        except Exception as e:
            self.queue.put((False, e))

    def is_finished(self):
        return self.queue.full()

    def get_result(self):
        return self.queue.get()

def timeout(secs):
    def wrapper(function):
        def _func(*args, **kwargs):
            proc = RunnableProcess(function, *args, **kwargs)
            proc.start()
            proc.join(secs)
            if proc.is_alive():
                proc.terminate()
                raise TimeoutException("timed out when running %s" % (str(function)))
            assert proc.is_finished()
            ok, res = proc.get_result()
            if ok:
                return res
            else:
                raise res
        return _func
    return wrapper


if __name__ == '__main__':
    u = time.time()
    print u
    s = utc2str(u)
    print s
    print str2utc(s)
    print _test_report_time(3)
