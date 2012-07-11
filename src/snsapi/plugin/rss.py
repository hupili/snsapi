#-*- encoding: utf-8 -*-

'''
RSS Feed Component

Supported Methods
    * auth() : 
        a NULL stub. 
    * home_timeline() : 
        read and parse RSS feed.
        pretend it to be a 'special' SNS platform, 
        where you can only read your wall but can 
        not write to it.
'''

from ..snsapi import SNSAPI
from ..snstype import Status,User
from ..third import feedparser

print "RSS Plugged!"

class RSSAPI(SNSAPI):
    def __init__(self, channel = None):
        super(RSSAPI, self).__init__()
        
        self.platform = "rss"
        self.domain = "null"

        ##just you remind myself they exists
        #self.app_key = ""
        #self.app_secret = ""
        ##you must set self.plaform before invoking read_config()
        #self.read_config()
        
        if channel: 
            self.read_channel(channel)
        else:
            #for backward compatibility
            self.read_config()
    
    def read_channel(self, channel):
        self.channel_name = channel['channel_name']
        self.url = channel['url']
        
    def auth(self):
        #Nothing to do.
        print "RSS platform do not need auth!"
        return 
        
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''

        #url = 'file:///home/hpl/Desktop/research/snsapi/test/sample-rss/feed1.xml'
        #url = 'file:///home/hpl/Desktop/research/snsapi/test/sample-rss/feed2.xml'
        #url = 'file://../test/feed.xml'
        #url = 'http://jason.diamond.name/weblog/feed/'
        d = feedparser.parse(self.url)
        
        statuslist = []
        for j in d['items']:
            statuslist.append(RSSStatus(j))
        return statuslist

        
class RSSStatus(Status):
    def parse(self, dct):
        self.username = dct['author']
        self.created_at = dct['published']
        self.title = dct['title']
        self.link = dct['link']
        
    def show(self):
        print "[%s] at %s \n  New article \"%s\" published! (%s)" % (self.username, self.created_at, self.title, self.link)
        #print "[%s] at %s \n  %s" % (self.username, self.created_at, self.text)
        #print "%s" % self.title
