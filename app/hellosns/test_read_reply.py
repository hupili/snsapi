# -*- coding: utf-8 -*-
'''
Read timeline from all configured channels and reply one

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

    status_list = sp.home_timeline()

    print "==== read messages from all channels ===="
    
    no = 0
    for s in status_list:
        print "--No. %d --" % no
        s.show()
        no = no + 1
        
    print "==== try to reply one ===="

    print "Input the no:"
    no = int(console_input())
    print "Input the text:"
    text = console_input()

    sID = status_list[no].ID
    print sp.reply(sID, text)
    
