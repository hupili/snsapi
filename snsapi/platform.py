# -*- coding: utf-8 -*-

'''
Platforms.

Upper layer can reference platforms from this module
'''

from plugin import *

# Comment/uncomment the following line to
# disable/enable trial plugins
from plugin_trial import *

import sys
import types
platform_list = []
__thismodule = sys.modules[__name__]
for n in dir():
    # do not include built-in names
    if n.find("__") == -1 and n.find("platform_list") == -1:
        # do not include module names
        if not type(getattr(__thismodule,n)) == types.ModuleType:
            platform_list.append(n)

#print platform_list
