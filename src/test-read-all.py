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
    #TODO:
    #this is a proof of concept
    #the following logic may be encapsulated in 
    #another container class later.

    #init channels using configurations in channel.json
    from os.path import abspath
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
                    plugin = getattr(snsapi, site['platform'])
                    mod = getattr(plugin, plugin._entry_class_)
                    if mod:
                        clis.append(mod(site))
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
        sl = c.home_timeline(5)
        for s in sl:
            s.show()
        print "=====End of channel: %s" % c.channel_name

