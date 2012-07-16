# -*- coding: utf-8 -*-

import snsapi
from snsapi import errors 
try:
    import json
except ImportError:
    import simplejson as json
from os.path import abspath
import sys

if __name__ == "__main__":
    #TODO:
    #this is a proof of concept
    #the following logic may be encapsulated in 
    #another container class later.

    fp = open(abspath('conf/forwarder.json'), "r")
    fconf = json.load(fp)
    print "channel_in ===== "
    for c in fconf['channel_in'] :
        print c
    print "channel_out ===== "
    for c in fconf['channel_out'] :
        print c
    
    sys.exit()

    #init channels using configurations in channel.json
    fname = abspath('conf/channel.json')
    clis = []
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
                        clis.append(snsapi.sina.SinaAPI(site))
                    elif site['platform'] == "rss":
                        clis.append(snsapi.rss.RSSAPI(site))
                    elif site['platform'] == "qq":
                        clis.append(snsapi.qq.QQAPI(site))
                    else:
                        raise errors.NoSuchPlatform
    except IOError:
        raise errors.NoConfigFile

    #authenticate all channels
    for c in clis:
        c.auth()

    #test home_timeline()
    for c in clis:
        print "=====Information from channel: %s" % c.channel_name
        sl = c.home_timeline()
        for s in sl:
            s.show()
        print "=====End of channel: %s" % c.channel_name

