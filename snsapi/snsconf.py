# -*- coding: utf-8 -*-

'''
snsapi Basic Hardcode Conf

See documentations of variables for more information.

For first time users, please ignore the following discussion in the same
section. They are intended for SNSAPI middleware developers. I don't 
want to confuse you at the moement. When you are ready to refactor this 
piece of code, you can come back to read them discuss in the group. 

This files may look weird at first glance, 
here's a short background story on how I 
get to this point:

   * There are many debugging information \
printed on the console previously, \
which make stdin/stdout interface a \
mess. 
   * I just developed a wrapper for logging. \
Hope it can unify different log messages. 
   * 'snsapi' as a whole package will import \
all plugins at the initialization stage. \
This will trigger a 'xxx plugged!" message.
   * Some calls to write logs happens before \
we have a chance to init SNSLog (Original \
plan is to let the upper layer init with \
its own preference). 
   * The workaround is to develop this \
hardcode conf files. 

Guidelines to add things here:

   * If something is to be configured before \
fully init of snsapi(which involves  \
init those plugins), the configuration  \
can go into this file. 
   * Otherwise, try best to let the upper \
layer configure it. Put the confs in the \
'../conf' folder. 

'''

from snslog import SNSLog

class SNSConf(object):
    """
    Hardcode Confs for SNSAPI

    """
    
    SNSAPI_CONSOLE_STDOUT_ENCODING = 'utf-8'

    '''
    See ``SNSAPI_CONSOLE_STDIN_ENCODING``.
    '''

    SNSAPI_CONSOLE_STDIN_ENCODING = 'utf-8'

    '''
    For chinese version windows systems, you may want to change 
    ``SNSAPI_CONSOLE_STDOUT_ENCODING = 'utf-8'``
    and
    ``SNSAPI_CONSOLE_STDIN_ENCODING = 'utf-8'``
    to 'gbk'. For others, check the encoding of 
    your console and set it accordingly. 

    See the discussion: https://github.com/hupili/snsapi/issues/8
    '''

    #SNSAPI_LOG_INIT_LEVEL = SNSLog.INFO
    SNSAPI_LOG_INIT_LEVEL = SNSLog.DEBUG

    '''
    Possible values: 
       * SNSLog.DEBUG
       * SNSLog.INFO
       * SNSLog.WARNING
       * SNSLog.ERROR
       * SNSLog.CRITICAL

    In Release version, set to WARNING
    '''

    #SNSAPI_LOG_INIT_VERBOSE = False
    SNSAPI_LOG_INIT_VERBOSE = True 

    '''
    Examples, 

    True:
       * [DEBUG][20120829-135506][sina.py][<module>][14]SinaAPI plugged! 

    False:
       * [DEBUG][20120829-142322]SinaAPI plugged! 
    '''

    #SNSAPI_LOG_INIT_LOGFILE = "snsapi.log"
    SNSAPI_LOG_INIT_LOGFILE = None

    '''
       * None: Output to STDOUT. Good for Debug version. 
       * {Filename}: Log to {Filename}. Good for Relase version. 
    '''

    def __init__(self, arg):
        raise
        

class SNSConfNoInstantiation(Exception):
    """
    This exception is used to make sure you do not 
    instantiate SNSConf class. 
    """
    def __init__(self):
        super(SNSConfNoInstantiation, self).__init__()

    def __str__(self):
        return "You can not instantiate SNSConf. "\
                "Call its static methods directly!"

# ========== Init Operations  =================

SNSLog.init(level = SNSConf.SNSAPI_LOG_INIT_LEVEL, \
        logfile = SNSConf.SNSAPI_LOG_INIT_LOGFILE, \
        verbose = SNSConf.SNSAPI_LOG_INIT_VERBOSE)
