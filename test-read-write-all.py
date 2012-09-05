# -*- coding: utf-8 -*-
        
if __name__ == "__main__":
    '''
    QQ weibo may fail sometimes, even with same input. May be the invoking frequency limit.
    Sina weibo is better, and more stable.
    '''

    sp = SNSPocket()
    sp.read_config()

    sp.auth()
    
    for cname in sp:
        print "listen first___________________________"
        sl = sp.home_timeline(channel = cname)
        print sl
        
        print "update status__________________________"
        print "Input text:"
        text = raw_input()
        ret = cli.update(text, channel = cname)
        print ret
