#-*- encoding: utf-8 -*-

'''
RSS2 Read/Write Component

Supported Methods
    * auth() : 
        Inherited from RSS
    * home_timeline() : 
        Inherited from RSS
    * update() :
        Publish new contents to a RSS2 feed
'''

from ..snslog import SNSLog 
logger = SNSLog
import datetime
from rss import RSSAPI, RSSStatus
from ..third import feedparser
from ..third import PyRSS2Gen
from ..snsapi import errors

_entry_class_ = "RSS2RWAPI"
logger.debug("%s plugged!", _entry_class_)

class RSS2RWAPI(RSSAPI):
    def __init__(self, channel = None):
        super(RSS2RWAPI, self).__init__()

        self.platform = "rss2rw"
        self.domain = "null"

        #default parameter for writing RSS2 feeds
        self.author = "snsapi"
        self.entry_timeout = 3600 #in seconds, default 1 hour

        if channel: 
            self.read_channel(channel)

    def read_channel(self, channel):
        super(RSS2RWAPI, self).read_channel(channel)
        if 'author' in channel:
            self.author = channel['author']
        if 'entry_timeout' in channel:
            self.entry_timeout = channel['entry_timeout']

    def auth(self):
        print "RSS2RW platform do not need auth!"
        return 

    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''
        d = feedparser.parse(self.url)

        statuslist = []
        for j in d['items']:
            if len(statuslist) >= count:
                break
            statuslist.append(RSS2RWStatus(j))
        return statuslist

    def update(self, text):
        '''
        Update the RSS2 feeds. 
        The file pointed to by self.url should be writable.
        Remember to set 'author' and 'entry_timeout' in configurations. 
        Or the default values are used. 
        @param text: messages to update in a feeds
        '''

        from dateutil import parser as dtparser, tz

        cur_time = datetime.datetime.now(tz.tzlocal())

        items = []

        #Read and filter existing entries.
        #Old entries are disgarded to keep the file short and clean.
        d = feedparser.parse(self.url)
        for j in d['items']:
            s = RSS2RWStatus(j)
            entry_time = dtparser.parse(s.created_at)
            if (cur_time - entry_time).seconds < self.entry_timeout:
                items.append( 
                    PyRSS2Gen.RSSItem(
                        author = s.username, 
                        title = s.title, 
                        description = "snsapi RSS2RW update",
                        pubDate = entry_time
                        )
                    )

        items.insert(0, 
            PyRSS2Gen.RSSItem(
                author = self.author, 
                title = text, 
                description = "snsapi RSS2RW update",
                pubDate = cur_time
                )
            )

        rss = PyRSS2Gen.RSS2(
            title = "snsapi, RSS2 R/W Channel",
            link = "https://github.com/uxian/snsapi",
            description = "RSS2 R/W channel based on feedparser and PyRSS2Gen",
            lastBuildDate = datetime.datetime.now(),
            items = items
            )

        try:
            rss.write_xml(open(self.url, "w"))
        except:
            raise errors.snsWriteFail

        return True

class RSS2RWStatus(RSSStatus):
    def parse(self, dct):
        super(RSS2RWStatus, self).parse(dct)

        #RSS2RW channel is intended for snsapi-standardized communication.
        #It does not have to digest RSS entry as is in RSSStatus. 
        #The 'title' field is the place where we put our messages. 
        self.text = self.title
        
    def show(self):
        print "[%s] at %s \n  %s" \
            % (self.username.encode('utf-8'), self.created_at.encode('utf-8'), \
            self.text.encode('utf-8'))
