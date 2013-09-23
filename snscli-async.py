#!/usr/bin/env python
import sys

if len(sys.argv) != 2:
    print "usage: %s {fn_async_db}" % sys.argv[0]
    sys.exit(-1)

if __name__ == '__main__':
    # sync-version CLI initialization
    from snscli import *
    load_config()
    list_channel()
    auth()

    # async facility setup
    from snsapi.snspocket import BackgroundOperationPocketWithSQLite
    fn_async_db = sys.argv[1]
    asp = BackgroundOperationPocketWithSQLite(sp, sys.argv[1])
    ht = home_timeline = asp.home_timeline
    up = update = convert_parameter_to_unicode(asp.update)
    re = reply = convert_parameter_to_unicode(asp.reply)
    fwd = forward = convert_parameter_to_unicode(asp.forward)

    logger.info("Ready to drop into the interactive shell of asynchronous SNSCLI!")
    import code
    code.interact(local=locals())
