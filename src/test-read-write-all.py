# -*- coding: utf-8 -*-

from snslog.snslog import SNSLog
logger = SNSLog
import snsapi
from snsapi import errors 
try:
    import json
except ImportError:
    import simplejson as json

def showStatus(ret):
    if ret == True:
        print "Success!"
        
    elif ret == False:
        print "Fail :("
        
    elif type(ret) == str:
        print ret

    elif type(ret) == dict:
        print ret

    elif type(ret) != list:
        ret.show()
    
    else:
        for s in ret:
            s.show()
            
        
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
                #print site['channel_name']
                #print site['open']
                #print site['platform']
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

    #For those platforms you want to test
    #configure them in 'conf/channel.json' now. 
    #accounts.append(snsapi.sina.SinaAPI())
    #accounts.append(snsapi.qq.QQAPI())
    
    for cli in accounts:
        cli.auth()
        
        print "listen first___________________________"
        sl = cli.home_timeline()
        showStatus(sl)
        
        print "update status__________________________"
        print "Input text:"
        text = raw_input()
        ret = cli.update(text)
        showStatus(ret)
    
