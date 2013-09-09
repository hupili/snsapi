# -*- coding: utf-8 -*-

'''
snsapi Log Tools
'''

import logging
import inspect
import os.path

#Test piece.
#This lambda expression does not "inline" into
#the caller file. The filename and funcname
#reported in log is still in 'snslog.py'
#mylog = lambda *x: logging.info(*x)

class SNSLog(object):
    """
    Provide the unified entry to write logs

    The current backend is Python's logging module.
    """

    #Static variables
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    VERBOSE = True

    def __init__(self):
        super(SNSLog).__init__()
        raise SNSLogNoInstantiation

    @staticmethod
    def init(logfile = None, level = WARNING, verbose = True):
        """
        Init the log basic configurations. It should
        be called only once over the entire execution.

        If you invoke it for multiple times, only the
        first one effects. This is the behaviour of
        logging module.

        """

        # Debug information writes to log using SNSLog.debug().
        # How do you debug the logger itself...?
        # Here it is...
        # We fall back to the print.
        # They should be comment out to make the screen clean.
        #print "=== init log ==="
        #print "logfile:%s" % logfile
        #print "level:%s" % level
        #print "verbose:%s" % verbose

        if logfile:
            logging.basicConfig(\
                    format='[%(levelname)s][%(asctime)s]%(message)s', \
                    datefmt='%Y%m%d-%H%M%S', \
                    level = level, \
                    filename = logfile
                    )
        else:
            logging.basicConfig(\
                    format='[%(levelname)s][%(asctime)s]%(message)s', \
                    datefmt='%Y%m%d-%H%M%S', \
                    level = level
                    )
        SNSLog.VERBOSE = verbose

    @staticmethod
    def __env_info():
        if SNSLog.VERBOSE:
            caller = inspect.stack()[2]
            fn = os.path.basename(caller[1])
            no = caller[2]
            func = caller[3]
            return "[%s][%s][%s]" % (fn, func, no)
        else:
            return ""

    @staticmethod
    def debug(fmt, *args):
        logging.debug(SNSLog.__env_info() + fmt, *args)

    @staticmethod
    def info(fmt, *args):
        logging.info(SNSLog.__env_info() + fmt, *args)

    @staticmethod
    def warning(fmt, *args):
        logging.warning(SNSLog.__env_info() + fmt, *args)

    @staticmethod
    def warn(fmt, *args):
        logging.warn(SNSLog.__env_info() + fmt, *args)

    @staticmethod
    def error(fmt, *args):
        logging.error(SNSLog.__env_info() + fmt, *args)

    @staticmethod
    def critical(fmt, *args):
        logging.critical(SNSLog.__env_info() + fmt, *args)

class SNSLogNoInstantiation(Exception):
    """docstring for SNSLogNoInstantiation"""
    def __init__(self):
        super(SNSLogNoInstantiation, self).__init__()

    def __str__(self):
        return "You can not instantiate SNSLog. "\
                "Call its static methods directly!"


if __name__ == '__main__':
    #SNSLog.init(level = SNSLog.DEBUG, verbose = False)
    SNSLog.init(level = SNSLog.DEBUG)
    SNSLog.warning('test: %d; %s', 123, "str")
    SNSLog.debug('test debug')
    SNSLog.info('test info')
    SNSLog.warning('test warning')
    SNSLog.warn('test warn')
    SNSLog.error('test error')
    SNSLog.critical('test critical')

