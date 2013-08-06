#!/usr/bin/env python -i
import sys
from snscli import *
from snsapi.snspocket import BackgroundOperationPocketWithSQLite
asp = BackgroundOperationPocketWithSQLite(sp, sys.argv[1])
ht = home_timeline = asp.home_timeline
up = update = convert_parameter_to_unicode(asp.update)
re = reply = convert_parameter_to_unicode(asp.reply)
fwd = forward = convert_parameter_to_unicode(asp.forward)
print "Make sure to run stop() before exiting."
print "Make sure to run stop() before exiting."
print "Make sure to run stop() before exiting."
print "Make sure to run stop() before exiting."
print "Make sure to run stop() before exiting."
def stop():
    asp.home_timeline_job.stop()
    asp.update_job.stop()
    print 'Exiting....'
    sys.exit(0)
