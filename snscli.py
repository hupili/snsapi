#!/usr/bin/env python
# -*- coding: utf-8 -*-

from snsapi.utils import console_output, console_input
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger

sp = SNSPocket()

import functools

def convert_parameter_to_unicode(func):
    '''
    Decorator to convert parameters to unicode if they are str

       * We use unicode inside SNSAPI.
       * If one str argument is found, we assume it is from console
         and convert it to unicode.

    This can solve for example:

       * The 'text' arg you give to ``update`` is not unicode.
       * You channel name contains non-ascii character, and you
         use ``ht(channel='xxx')`` to get the timeline.
    '''
    def to_unicode(s):
        if isinstance(s, str):
            return console_input(s)
        else:
            return s
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = map(lambda x: to_unicode(x), args)
        new_kwargs = dict(map(lambda x: (x[0], to_unicode(x[1])), kwargs.items()))
        return func(*new_args, **new_kwargs)
    return wrapper

# Shortcuts for you to operate in Python interactive shell

lc = load_config = sp.load_config
sc = save_config =  sp.save_config
lsc = list_channel =  sp.list_channel
lsp = list_platform =  sp.list_platform
newc = new_channel = sp.new_channel
addc = add_channel = sp.add_channel
clc = clear_channel = sp.clear_channel
auth = auth = sp.auth
ht = home_timeline = convert_parameter_to_unicode(sp.home_timeline)
up = update = convert_parameter_to_unicode(sp.update)
re = reply = convert_parameter_to_unicode(sp.reply)
fwd = forward = convert_parameter_to_unicode(sp.forward)

#==== documentation ====

helpdoc = \
"""
snscli -- the interactive CLI to operate all SNS!

Type "print helpdoc" again to see this document.

To start your new journey, type "print tut"

   * lc = load_config
   * sc = save_config
   * lsc = list_channel
   * lsp = list_platform
   * newc = new_channel
   * addc = add_channel
   * clc = clear_channel
   * auth = auth
   * ht = home_timeline
   * up = update
   * re = reply
   * fwd = forward

Tutorial of SNSCLI:

   * https://github.com/hupili/snsapi/wiki/Tutorial-of-snscli
"""

if __name__ == '__main__':
    #==== default initialization one may like ====
    print helpdoc
    load_config()
    list_channel()
    auth()

    logger.info("Ready to drop into the interactive shell of SNSCLI!")
    import code
    code.interact(local=locals())
