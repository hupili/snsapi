# -*- coding: utf-8 -*-

from snslog.snslog import SNSLog
logger = SNSLog
import snsapi
from snsapi import errors 
try:
    import json
except ImportError:
    import simplejson as json
        
if __name__ == "__main__":
    '''
    QQ weibo may fail sometimes, even with same input. May be the invoking frequency limit.
    Sina weibo is better, and more stable.
    '''
    accounts = []
    from os.path import abspath
    fname = abspath('conf/channel.json')
    try:
        with open(fname, "r") as fp:
            allinfo = json.load(fp)
            for site in allinfo:
                print "===channel:%s;open:%s;platform:%s" % \
                        (site['channel_name'],site['open'],site['platform'])
                if site['open'] == "yes" :
                    plugin = getattr(snsapi, site['platform'])
                    mod = getattr(plugin, plugin._entry_class_)
                    if mod:
                        accounts.append(mod(site))
                    else:
                        raise errors.NoSuchPlatform
    except IOError:
        raise errors.NoConfigFile
    
    print "==== auth all the channels ====" 
    for cli in accounts:
        cli.auth()
        
    print "==== get all home_timeline (each 5 entries) ===="
    status_list = []
    for cli in accounts:
        sl = cli.home_timeline(20)
        status_list.extend(sl)

    no = 0 
    for s in status_list:
        print "--No. %d --" % no
        s.show()
        no = no + 1
        #print "-----------"
        
    print "==== try to reply one ===="

    print "Input the no:"
    no = int(raw_input())
    print "Input the text:"
    text = raw_input()

    #print text
    #pass
    #no = 0
    #text = "test reply function" 
    #no = 0
    #text = "(微笑)" 
    #print type(text)
    #print isinstance(text, unicode)
    #text = "(%E5%BE%AE%E7%AC%91)" 

    sID = status_list[no].ID
    for cli in accounts:
        if cli.platform == sID.platform:
            #ret = cli.reply(sID, text.encode('utf8'))
            #ret = cli.reply(sID, text.decode('utf-8'))
            ret = cli.reply(sID, text)
            print ret
            break

    #ret = cli.update(text)
    #showStatus(ret)
    
