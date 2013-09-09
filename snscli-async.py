#!/usr/bin/env python -i
import sys
from snscli import *
from snsapi.snspocket import BackgroundOperationPocketWithSQLite
import atexit
asp = BackgroundOperationPocketWithSQLite(sp, sys.argv[1])
ht = home_timeline = asp.home_timeline
up = update = convert_parameter_to_unicode(asp.update)
re = reply = convert_parameter_to_unicode(asp.reply)
fwd = forward = convert_parameter_to_unicode(asp.forward)
