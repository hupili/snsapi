# -*- coding: utf-8 -*-
'''
myword 

'''

#from snsapi.plugin.renren import RenrenAPI
from snsapi.snspocket import SNSPocket
import json
import sys
import urllib2
import hashlib
import time

REPLY_GAP = 10 # seconds, 10 seems the minimum
NEWS_QUERY_COUNT = 5
MY_NAME = "hsama2012"

def can_reply(status):
    """
    A filter function of the status you want to reply
    """
    if not status.parsed.text.find("@" + MY_NAME) == -1:
        return True
    else:
        return False
        
        
def get_word(text):
    """
    To the get word in a message
    """
    text = text.replace("@" + MY_NAME +" ","")
    return text 
    
    
def translate(word):
    """
    Translate a word with dic.zhan-dui.com
    """
    url = "http://dic.zhan-dui.com/api.php?s=" + word + "&type=json"
    req = urllib2.Request(url, data='')
    req.add_header('User_Agent', 'toolbar')
    results = json.load(urllib2.urlopen(req))
    if "error_code" in results:
        return word +" " + " not found"
    else:
        mean = ""
        for c in results["simple_dic"]:
            mean = mean + c
        return word + " " + mean
    
    
    

def main():
    """docstring for main"""
    #set system default encoding to utf-8 to avoid encoding problems
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    
    #load channel configurations
    channels = json.load(open('conf/channel.json'))
    
    

    #find one account
    rr = SNSPocket()
    for c in channels:
        rr.add_channel(c)

    if rr is None:
        print "cannot find one renren platform in channel.json"
        return 
    else:
        rr.load_config()
        rr.auth()
        

    #load record to avoid repeated reply
    try:
        sIDs = json.load(open('statusID.json'))
    except IOError, e:
        if e.errno == 2: #no such file
            sIDs = {}
        else:
            raise e

    status_list = rr.home_timeline(NEWS_QUERY_COUNT)
    for s in status_list:
        s.show()
        msg_string = "".join( unicode(x) for x in \
                [s.parsed.time, s.ID, s.parsed.username, \
                s.parsed.userid, s.parsed.text])
        sig = hashlib.sha1(msg_string.encode('utf-8')).hexdigest()
        if not sig in sIDs and can_reply(s):
            print '[reply it]'
            REPLY_STRING = translate(get_word(s.parsed.text))
            ret = rr.reply(s.ID, REPLY_STRING.decode('utf-8'))
            print "[ret: %s]" % ret
            print "[wait for %d seconds]" % REPLY_GAP
            time.sleep(REPLY_GAP)
            if ret:
                sIDs[sig] = msg_string
        else: 
            print '[no reply]'

    #save reply record
    json.dump(sIDs, open('statusID.json', 'w'))

if __name__ == '__main__':
    main()
