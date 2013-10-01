#-*- encoding: utf-8 -*-
import snsconf
import snslog
import utils
import snstype
from errors import snserror
#import snscrypt
#from third import *

import platform

_dir_static_data = snsconf.SNSConf._SNSAPI_DIR_STATIC_DATA

__versioninfo__ = (0, 7, 0)
__version__ = '.'.join(map(str, __versioninfo__))
