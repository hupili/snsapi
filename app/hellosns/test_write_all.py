# -*- coding: utf-8 -*-
'''
Update status on all channels

docstring placeholder
'''

from snsapi.snspocket import SNSPocket
from snsapi.utils import console_input,console_output
        
if __name__ == "__main__":
    '''
    QQ weibo may fail sometimes, even with same input. May be the invoking frequency limit.
    Sina weibo is better, and more stable.
    '''

    sp = SNSPocket()
    sp.load_config()

    sp.auth()
    
    for cname in sp:
        print "listen first___________________________%s" % cname
        sl = sp.home_timeline(channel = cname)
        print sl
        
        print "update status__________________________%s" % cname
        print "Input text:"
        text = raw_input()
        ret = sp.update(text, channel = cname)
        print ret
