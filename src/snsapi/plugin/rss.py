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

_entry_class_ = "RSSAPI"

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
            if len(statuslist) >= count:
                break
            statuslist.append(RSSStatus(j))
        return statuslist

        
class RSSStatus(Status):
    def __get_dict_entry(self, attr, dct, field):
        #dict entry reading with fault tolerance. 
        #  self.attr = dct['field']
        #RSS format is very diverse. 
        #To my current knowledge, some format have 
        #'author' fields, but others do not:
        #   * rss : no
        #   * rss2 : yes
        #   * atom : yes
        #   * rdf : yes
        #This function will return a string "(null)"
        #by default if the field does not exist. 
        #The purpose is to expose unified interface
        #to upper layers. (seeing "(null)" is better 
        #than catching an error. 
        try:
            setattr(self, attr, dct[field])
        except KeyError:
            setattr(self, attr, "(null)")
        
    def parse(self, dct):
        #self.username = dct['author']
        ##self.created_at = dct['published']
        ##For RSS, one entry will be brought up if it is updated. 
        ##We use it as 'created_at' field of SNS stauts. 
        ##This is for better message deduplicate
        #self.created_at = dct['updated']
        #self.title = dct['title']
        #self.link = dct['link']

        self.__get_dict_entry('username', dct, 'author')
        self.__get_dict_entry('created_at', dct, 'updated')
        self.__get_dict_entry('title', dct, 'title')
        self.__get_dict_entry('link', dct, 'link')

        #other plugins have 'text' field
        self.text = "Article \"%s\" is updated(published)! (%s)" % (self.title, self.link)
        
    def show(self):
        print "[%s] at %s \n  Article \"%s\" is updated(published)! (%s)" \
            % (self.username.encode('utf-8'), self.created_at.encode('utf-8'), \
            self.title.encode('utf-8'), self.link.encode('utf-8'))
