# -*- coding: utf-8 -*-

import time
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

    try:
        messages = json.load(open('messages.json'))
    except IOError, e:
        if e.errno == 2: #no such file
            messages = {}
        else:
            raise e

    #load message information and check in channels. 
    #merge new messages into local storage
    #messages = json.load(open(abspath('messages.json'),'r'))
    for cin_name in channel_in :
        print "==== Reading channel: %s" % (cin_name)
        cin_obj = channels[cin_name]
        #TODO: make it configurable for each channel
        sl = cin_obj.home_timeline(2)
        for s in sl:
            #s.show()
            #print type(s.created_at)
            #print type(s.username)
            #print type(s.text)
            msg_full = unicode(s.created_at) + unicode(s.username) + unicode(s.text)
            sig = hashlib.sha1(msg_full.encode('utf-8')).hexdigest()
            #sig = hashlib.sha1(msg_full).hexdigest() # <-- this line will raise an error
            if sig in messages:
                print "One duplicate message:%s" % (sig)
            else:
                print ">>>New message"
                s.show()
                messages[sig] = {
                    'sig': sig,
                    'created_at': s.created_at,
                    'username': s.username,
                    'text': s.text,
                    'success':{"__null":"yes"}
                }
                #The message is new
                #forward it to all output channels

    #set quota/run for each out_channel 
    #TODO: make it configurable
    quota = {}
    for c in channel_out :
        quota[c] = 1

    #forward non-successful messages to all out_channels
    for m in messages :
        #break
        for cout_name in quota :
            if cout_name in messages[m]['success'] and messages[m]['success'][cout_name] == "yes":
                pass
            else:
                if quota[cout_name] > 0:
                    quota[cout_name] -= 1 
                    cout_obj = channels[cout_name]
                    #text = "[%s] at %s \n %s"  % (s.username, s.created_at, s.text)
                    #text = "[%s] at %s \n %s (forward time:%s)"  % (s.username, s.created_at, s.text, time.time())
                    s = messages[m]
                    print "forwarding %s to %s" % (m, cout_name)
                    text = "[%s] at %s \n %s (forward time:%s)"  % (s['username'], s['created_at'], s['text'], time.time())
                    print "Text: %s" % (text)
                    #TODO: check the real cause of the problem.
                    #      It is aleady announec in the front of this file 
                    #      that all strings should be treated as UTF-8 encoding. 
                    #      Why do the following problem happen?
                    if ( cout_obj.update(text.encode('utf-8')) ):
                        messages[m]['success'][cout_name] = "yes"
                        print "Forward success: %s" % (sig)
                    else:
                        messages[m]['success'][cout_name] = "no"
                        print "Forward fail: %s" % (sig)

    print "forwarding done!"
    #print messages

    json.dump(messages, open('messages.json','w')) 
    #json.dumps({'1':2,3:4})
    sys.exit()

