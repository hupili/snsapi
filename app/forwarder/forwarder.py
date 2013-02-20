# -*- coding: utf-8 -*-
'''
forwarder (SNSAPI Sample Application)

introduction placeholder
'''

import time
from os.path import abspath

import snsapi
from snsapi import errors 
from snsapi import utils as snsapi_utils
from snsapi.utils import json
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger

class Forwarder(object):
    def __init__(self, fn_channel = "conf/channel.json", 
            fn_forwarder = "conf/forwarder.json",
            fn_message = "messages.json"):
        super(Forwarder, self).__init__()

        self.fn_channel = fn_channel
        self.fn_forwarder = fn_forwarder
        self.fn_message = fn_message
        self.load_config(fn_channel, fn_forwarder)
        self.db_init()

    def db_init(self):
        try:
            self.messages = json.load(open(self.fn_message))
        except IOError, e:
            if e.errno == 2: #no such file
                self.messages = {}
            else:
                raise e

    def db_save(self):
        from snsapi.utils import JsonDict
        dct = JsonDict(self.messages)
        open(self.fn_message,'w').write(dct._dumps_pretty())

    def db_add(self, msg):
        '''
        msg: the snsapi.Message object
        '''
        sig = msg.digest()
        if sig in self.messages:
            logger.debug("One duplicate message: %s", sig)
        else:
            logger.debug("New message: %s", str(msg))
            self.messages[sig] = {
                'sig': sig,
                'time': msg.parsed.time,
                'username': msg.parsed.username,
                'text': msg.parsed.text,
                'success': {"__null": "yes"}
            }

    def db_get_message(self):
        '''
        Pick one message that is not forwarded (successfully). Returen a 
        list of <channel_name, msg> pairs. If the intended out channel is  
        limited in quota, we do not append it. 
        '''
        ret = []
        for (sig, msg) in self.messages.iteritems():
            for (cn, quota)  in self.jsonconf['quota'].iteritems():
                if cn in self.messages[sig]['success'] and self.messages[sig]['success'][cn] == "yes":
                    pass
                else:
                    if quota > 0:
                        self.jsonconf['quota'][cn] -= 1 
                        ret.append((cn, msg))
        return ret

    def _copy_channels(self, src, dst, names):
        for cn in names:
            if src.get(cn, None):
                dst[cn] = src[cn]

    def _set_default_quota(self):
        if not 'quota' in self.jsonconf:
            self.jsonconf['quota'] = {}
        for cn in self.sp_out:
            if not cn in self.jsonconf['quota']:
                self.jsonconf['quota'][cn] = 1

    def load_config(self, fn_channel, fn_forwarder):
        self.sp_all = SNSPocket()
        self.sp_all.load_config(fn_channel)
        self.sp_in = SNSPocket()
        self.sp_out = SNSPocket()
        try:
            self.jsonconf = json.load(open(fn_forwarder))
            self._copy_channels(self.sp_all, self.sp_in, self.jsonconf['channel_in'])
            self._copy_channels(self.sp_all, self.sp_out, self.jsonconf['channel_out'])
            self._set_default_quota()
        except IOError, e:
            logger.warning("Load '%s' failed, use default: no in_channel and out_channel", fn_forwarder)
            # Another possible handle of this error instead of default
            #raise errors.NoConfigFile
        logger.info("SNSPocket for all: %s", self.sp_all)
        logger.info("SNSPocket for in channel: %s", self.sp_in)
        logger.info("SNSPocket for out channel: %s", self.sp_out)

    def auth(self, *args, **kargs):
        return self.sp_all.auth(*args, **kargs)

    def home_timeline(self, *args, **kargs):
        return self.sp_in.home_timeline(*args, **kargs)

    def update(self, *args, **kargs):
        return self.sp_out.update(*args, **kargs)

    def format_msg(self, msg):
        return "[%s] at %s \n %s (fwd at:%s)"  % (msg['username'], msg['time'], msg['text'], time.time())

    def forward(self):
        sl = self.home_timeline()
        for s in sl:
            self.db_add(s)
        for (cn, msg) in self.db_get_message():
            text = self.format_msg(msg) 
            r = self.sp_out[cn].update(text)
            msg['success'][cn] = "yes" if r else "no"
            logger.info("forward '%s' -- %s", text, r)
                
if __name__ == "__main__":
    fwd = Forwarder()
    fwd.auth()
    #print fwd.home_timeline()
    #print fwd.update('hello')
    #print fwd.sp_out.home_timeline()
    #print fwd.jsonconf
    fwd.forward()
    fwd.db_save()
