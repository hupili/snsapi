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
     ``../conf`` folder.

'''

from os import path

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

    SNSAPI_LOG_INIT_LEVEL = SNSLog.INFO

    '''
    Possible values:
       * SNSLog.DEBUG
       * SNSLog.INFO
       * SNSLog.WARNING
       * SNSLog.ERROR
       * SNSLog.CRITICAL

    In Release version, set to WARNING
    '''

    SNSAPI_LOG_INIT_VERBOSE = False

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

    #TODO:
    #    Find better way to organize static package data
    _SNSAPI_DIR_STATIC_DATA = path.join(path.dirname(path.abspath(__file__)), 'data')
    _USER_HOME = path.expanduser('~')
    _SNSAPI_DIR_USER_ROOT = path.join(_USER_HOME, '.snsapi')
    _SNSAPI_DIR_CWD = path.abspath('.')
    if path.isdir(path.join(_SNSAPI_DIR_CWD, 'conf'))\
        and path.isdir(path.join(_SNSAPI_DIR_CWD, 'save')):
        SNSAPI_DIR_STORAGE_ROOT = _SNSAPI_DIR_CWD
    else:
        SNSAPI_DIR_STORAGE_ROOT = _SNSAPI_DIR_USER_ROOT
    SNSAPI_DIR_STORAGE_CONF = path.join(SNSAPI_DIR_STORAGE_ROOT, 'conf')
    SNSAPI_DIR_STORAGE_SAVE = path.join(SNSAPI_DIR_STORAGE_ROOT, 'save')

    '''
    ``SNSAPI_DIR_STORAGE_ROOT`` can be:

       * ``./``: if there exists ``./save`` and ``./conf``.
         This is the usual case for running SNSAPI under the repo.
         We have the two dirs by default.
         In this way, you can have multiple configurations on your machine at the same time.
       * ``~/.snsapi/``: if the above condition is not satisfied.
         This is to allow users to launch applications
         (e.g. ``snscli.py`` and ``snsgui.py``)
         from any place in the system.
         The per-user configurations and saved credentials can be used.

    ``SNSAPI_DIR_STORAGE_CONF`` and ``SNSAPI_DIR_STORAGE_SAVE``
    are just subdir "conf" and "save" under
    ``SNSAPI_DIR_STORAGE_ROOT``
    '''

    import os
    if not path.isdir(SNSAPI_DIR_STORAGE_ROOT):
        os.mkdir(SNSAPI_DIR_STORAGE_ROOT)
    if not path.isdir(SNSAPI_DIR_STORAGE_CONF):
        os.mkdir(SNSAPI_DIR_STORAGE_CONF)
    if not path.isdir(SNSAPI_DIR_STORAGE_SAVE):
        os.mkdir(SNSAPI_DIR_STORAGE_SAVE)


    def __init__(self):
        raise SNSConfNoInstantiation()


class SNSConfNoInstantiation(Exception):
    """
    This exception is used to make sure you do not
    instantiate SNSConf class.
    """
    def __init__(self):
        super(SNSConfNoInstantiation, self).__init__()

    def __str__(self):
        return "You can not instantiate SNSConf. "\
                "Access its static members directly!"

try:
    #NOTE:
    #    `set_custom_conf`` is a callable which modifies `SNSConf` class.
    #    e.g. developers can set
    import custom_conf
    custom_conf.set_custom_conf(SNSConf)
except:
    pass

# ========== Init Operations  =================

SNSLog.init(level = SNSConf.SNSAPI_LOG_INIT_LEVEL, \
        logfile = SNSConf.SNSAPI_LOG_INIT_LOGFILE, \
        verbose = SNSConf.SNSAPI_LOG_INIT_VERBOSE)
