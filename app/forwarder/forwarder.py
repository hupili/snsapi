# -*- coding: utf-8 -*-

import time
from os.path import abspath
import sys

import snsapi
from snsapi import errors 
from snsapi.utils import json
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger

class Forwarder(object):
    def __init__(self, fn_channel = "conf/channel.json", 
            fn_forwarder = "conf/forwarder.json"):
        super(Forwarder, self).__init__()

        self.load_config(fn_channel, fn_forwarder)
        self.init_db()

    def init_db(self):
        try:
            self.messages = json.load(open('messages.json'))
        except IOError, e:
            if e.errno == 2: #no such file
                messages = {}
            else:
                raise e

    def _copy_channels(self, src, dst, names):
        for cn in names:
            if src.get(cn, None):
                dst[cn] = src[cn]

    def load_config(self, fn_channel, fn_forwarder):
        self.sp_all = SNSPocket()
        self.sp_all.load_config(fn_channel)
        self.sp_in = SNSPocket()
        self.sp_out = SNSPocket()
        try:
            self.jsonconf = json.load(open(fn_forwarder))
            self._copy_channels(self.sp_all, self.sp_in, self.jsonconf['channel_in'])
            self._copy_channels(self.sp_all, self.sp_out, self.jsonconf['channel_out'])
        except IOError, e:
            logger.warning("Load '%s' failed, use default: no in_channel and out_channel", fn_forwarder)
            # Another possible handle of this error instead of default
            #raise errors.NoConfigFile

    def auth(self, *args, **kargs):
        return self.sp_all.auth(*args, **kargs)

    def home_timeline(self, *args, **kargs):
        return self.sp_in.home_timeline(*args, **kargs)

    def update(self, *args, **kargs):
        return self.sp_out.update(*args, **kargs)


if __name__ == "__main__":
    fwd = Forwarder()
    print fwd.sp_all
    print fwd.sp_in
    print fwd.sp_out
    fwd.auth()
    print fwd.home_timeline()
    print fwd.update('hello')

    sys.exit()

    # ======== below is the old code =====

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

