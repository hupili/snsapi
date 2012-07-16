# -*- coding: utf-8 -*-

import hashlib
import snsapi
from snsapi import errors 
try:
    import json
except ImportError:
    import simplejson as json
from os.path import abspath
import sys

def channel_init(fn_channel):
    fname = abspath(fn_channel)
    channels = {}
    try:
        with open(fname, "r") as fp:
            allinfo = json.load(fp)
            for site in allinfo:
                print "=== channel:%s;open:%s;platform:%s" % \
                        (site['channel_name'],site['open'],site['platform'])
                if site['open'] == "yes" :
                    #TODO: the following code seems clumsy
                    #any way to simplify it? 
                    #e.g. use the string name to the the corresponding class directly
                    if site['platform'] == "sina" :
                        #clis.append(snsapi.sina.SinaAPI(site))
                        channels[site['channel_name']] = snsapi.sina.SinaAPI(site)
                    elif site['platform'] == "rss":
                        #clis.append(snsapi.rss.RSSAPI(site))
                        channels[site['channel_name']] = snsapi.rss.RSSAPI(site)
                    elif site['platform'] == "qq":
                        #clis.append(snsapi.qq.QQAPI(site))
                        channels[site['channel_name']] = snsapi.qq.QQAPI(site)
                    else:
                        raise errors.NoSuchPlatform
            return channels
    except IOError:
        raise errors.NoConfigFile


if __name__ == "__main__":

    channels = channel_init('conf/channel.json') ;
    #authenticate all channels
    for cname in channels:
        channels[cname].auth()

    fp = open(abspath('conf/forwarder.json'), "r")
    fconf = json.load(fp)
    channel_in = fconf['channel_in']
    channel_out = fconf['channel_out']
    print "channel_in ===== "
    for c in channel_in :
        print c
    print "channel_out ===== "
    for c in channel_out :
        print c

    #print "test channel_in ===== "
    messages = json.load(open(abspath('messages.json'),'r'))
    for cin_name in channel_in :
        print "==== Reading channel: %s" % (cname)
        cin_obj = channels[cin_name]
        sl = cin_obj.home_timeline()
        for s in sl:
            sig = hashlib.sha1(s.created_at + s.username + s.text).hexdigest()
            if sig in messages:
                print "One duplicate message:%s" % (sig)
            else:
                print ">>>New message"
                s.show()
                messages[sig] = {
                    'sig': sig,
                    'created_at': s.created_at,
                    'username': s.username,
                    'text': s.text
                }
                #The message is new
                #forward it to all output channels
                for cout_name in channel_out :
                    cout_obj = channels[cout_name]
                    text = "[%s] at %s \n %s"  % (s.username, s.created_at, s.text)
                    print "Text: %s" % (text)
                    if ( cout_obj.update(text) ):
                        print "Forward success: %s" % (sig)
                    else:
                        print "Forward fail: %s" % (sig)

    print "forwarding done!"
    #print messages

    json.dump(messages, open('messages.json','w')) 
    #json.dumps({'1':2,3:4})
    sys.exit()

