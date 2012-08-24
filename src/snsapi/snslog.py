# -*- coding: utf-8 -*-

'''
snsapi Log Tools
'''

import logging

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

    def __init__(self):
        super(SNSLog).__init__()
        raise SNSLogNoInstantiation

    @staticmethod
    def init(fname = None, level = WARNING):
        """
        Init the log basic configurations. It should 
        be called only once over the entire execution. 
        
        If you invoke it for multiple times, only the 
        first one effects. This is the behaviour of 
        logging module. 
        
        """
        logging.basicConfig(\
                format='[%(levelname)s][%(asctime)s][%(filename)s][%(funcName)s]%(message)s', \
                datefmt='%Y%m%d-%H%M%S', \
                level = level
                )

    @staticmethod
    def debug(fmt, *args):
        logging.debug(fmt, *args)

    @staticmethod
    def info(fmt, *args):
        logging.info(fmt, *args)

    @staticmethod
    def warning(fmt, *args):
        logging.warning(fmt, *args)

    @staticmethod
    def warn(fmt, *args):
        logging.warn(fmt, *args)

    @staticmethod
    def error(fmt, *args):
        logging.error(fmt, *args)
        
    @staticmethod
    def critical(fmt, *args):
        logging.critical(fmt, *args)

class SNSLogNoInstantiation(Exception):
    """docstring for SNSLogNoInstantiation"""
    def __init__(self):
        super(SNSLogNoInstantiation, self).__init__()

    def __str__(self):
        return "You can not instantiate SNSLog. "\
                "Call its static methods directly!"
       


#TODO:
# To enable project wide Debugging by default
# This line should be commented out normally
SNSLog.init(level = SNSLog.DEBUG)

if __name__ == '__main__':
    SNSLog.init(level = SNSLog.DEBUG)
    SNSLog.warning('test: %d; %s', 123, "str")
    SNSLog.debug('test debug')
    SNSLog.info('test info')
    SNSLog.warning('test warning')
    SNSLog.warn('test warn')
    SNSLog.error('test error')
    SNSLog.critical('test critical')


