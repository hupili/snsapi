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

_entry_class_ = "RSS2RWAPI"

#from ..snsapi import SNSAPI
#from ..snstype import Status,User
import datetime
from rss import RSSAPI, RSSStatus
from ..third import feedparser
from ..third import PyRSS2Gen
from ..snsapi import errors

print "RSS2RW Plugged!"

class RSS2RWAPI(RSSAPI):
    def __init__(self, channel = None):
        super(RSS2RWAPI, self).__init__()

        self.platform = "rss2rw"
        self.domain = "null"
        self.author = "snsapi"

        if channel: 
            self.read_channel(channel)

    def read_channel(self, channel):
        super(RSS2RWAPI, self).read_channel(channel)
        if 'author' in channel:
            self.author = channel['author']

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
            statuslist.append(RSSStatus(j))
        return statuslist

    def update(self, text):
        '''
        Update the RSS2 feeds. 
        The file pointed to by self.url should be writable.
        @param text: messages to update in a feeds
        '''

        items = [ 
            PyRSS2Gen.RSSItem(
                author = "test", 
                title = "PyRSS2Gen-0.0 released",
                link = "http://www.dalkescientific.com/news/030906-PyRSS2Gen.html",
                description = "Dalke Scientific today announced PyRSS2Gen-0.0, "
                "a library for generating RSS feeds for Python.  ",
                guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/news/"
                    "030906-PyRSS2Gen.html"),
                pubDate = datetime.datetime(2003, 9, 6, 21, 31)),
            ]  
        rss = PyRSS2Gen.RSS2(
            title = "Andrew's PyRSS2Gen feed",
            link = "http://www.dalkescientific.com/Python/PyRSS2Gen.html",
            description = "The latest news about PyRSS2Gen, a "
            "Python library for generating RSS2 feeds",

            lastBuildDate = datetime.datetime.now(),
            items = items
            )

        try:
            rss.write_xml(open(self.url, "w"))
        except:
            raise errors.snsWriteFail

        return True

