# -*- coding: utf-8 -*-
'''
mysofa (SNSAPI Sample Application)

introduction placeholder

**Warning: The code is under reconstruction using new SNSAPI interface. 
Do not use this app until it is done.**
'''

#from snsapi.plugin.renren import RenrenAPI
import json
import hashlib
import time

MYSOFAR_REPLY_STRING = "(微笑)"
MYSOFAR_REPLY_GAP = 10 # seconds, 10 seems the minimum
MYSOFAR_NEWS_QUERY_COUNT = 1

def can_reply(status):
    """
    A filter function of the status you want to reply
    """
    if status.username.count('hpl'):
        return True
    else:
        return False

def main():
    """docstring for main"""

    #load channel configurations
    channels = json.load(open('conf/channel.json'))

    #find one renren account
    rr = None
    for c in channels:
        if c['platform'] == "renren":
            rr = RenrenAPI(c)

    if rr is None:
        print "cannot find one renren platform in channel.json"
        return 
    else:
        rr.auth()

    #load record to avoid repeated reply
    try:
        sIDs = json.load(open('statusID.json'))
    except IOError, e:
        if e.errno == 2: #no such file
            sIDs = {}
        else:
            raise e

    status_list = rr.home_timeline(MYSOFAR_NEWS_QUERY_COUNT)
    for s in status_list:
        s.show()
        msg_string = "".join( unicode(x) for x in \
                [s.created_at, s.username, s.text, \
                s.ID.platform, s.ID.status_id, s.ID.source_user_id])
        sig = hashlib.sha1(msg_string.encode('utf-8')).hexdigest()
        if not sig in sIDs and can_reply(s):
            print '[reply it]'
            ret = rr.reply(s.ID, MYSOFAR_REPLY_STRING)
            print "[ret: %s]" % ret
            print "[wait for %d seconds]" % MYSOFAR_REPLY_GAP
            time.sleep(MYSOFAR_REPLY_GAP)
            if ret:
                sIDs[sig] = msg_string
        else:
            print '[no reply]'

    #save reply record
    json.dump(sIDs, open('statusID.json', 'w'))

if __name__ == '__main__':
    main()
