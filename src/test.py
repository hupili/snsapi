# -*- coding: utf-8 -*-

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
                    #TODO: the following code seems clumsy
                    #any way to simplify it? 
                    #e.g. use the string name to the the corresponding class directly
                    if site['platform'] == "sina" :
                        accounts.append(snsapi.sina.SinaAPI(site))
                    elif site['platform'] == "rss":
                        #dummy operation to keep the conditional
                        #branch here.... 
                        ____tmp = 1
                        #the test of update() here is not supported 
                        #by RSS channels. 
                        #Design some way for the app layer to test 
                        #supported methods later
                        #clis.append(snsapi.rss.RSSAPI(site))
                    elif site['platform'] == "qq":
                        accounts.append(snsapi.qq.QQAPI(site))
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
    
