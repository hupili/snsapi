#!/usr/bin/env python -i
import sys

if len(sys.argv) != 2:
    print "usage: %s {fn_async_db}" % sys.argv[0]
    sys.exit(-1)
else:
    from snscli import *
    from snsapi.snspocket import BackgroundOperationPocketWithSQLite
    fn_async_db = sys.argv[1]
    asp = BackgroundOperationPocketWithSQLite(sp, sys.argv[1])
    ht = home_timeline = asp.home_timeline
    up = update = convert_parameter_to_unicode(asp.update)
    re = reply = convert_parameter_to_unicode(asp.reply)
    fwd = forward = convert_parameter_to_unicode(asp.forward)
