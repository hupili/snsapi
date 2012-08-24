# -*- coding: utf-8 -*-

'''
snsapi Basic Hardcode Conf

This files may look weird at first glance, 
here's a short background story on how I 
get to this point:
   * There are many debugging information 
   printed on the console previously, 
   which make stdin/stdout interface a 
   mess. 
   * I just developed a wrapper for logging.
   Hope it can unify different log messages. 
   * 'snsapi' as a whole package will import 
   all plugins at the initialization stage. 
   This will trigger a 'xxx plugged!" message.
   * Some calls to write logs happens before
   we have a chance to init SNSLog (Original
   plan is to let the upper layer init with 
   its own preference). 
   * The workaround is to develop this 
   hardcode conf files. 

Guidelines to add things here:
   * If something is to be configured before
   fully init of snsapi(which involves 
   init those plugins), the configuration 
   can go into this file. 
   * Otherwise, try best to let the upper
   layer configure it. Put the confs in the
   '../conf' folder. 
'''

# ========== logging confs =================

from snslog import SNSLog

#Debug level, print to console, for developers
SNSLog.init(level = SNSLog.DEBUG)

#Warning level, print to logfile, for release versions
#SNSLog.init(logfile = "snsapi.log", verbose = False)

#SNSLog.init(level = SNSLog.DEBUG, logfile = "snsapi.log", verbose = False)

# ========== console confs =================

SNSAPI_CONSOLE_STDOUT_ENCODING = 'utf-8'
