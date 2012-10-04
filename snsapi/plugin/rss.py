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


from ..snslog import SNSLog 
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype
from ..third import feedparser
import datetime
from ..third import PyRSS2Gen
from ..errors import snserror

logger.debug("%s plugged!", __file__)

class RSS(SNSBase):
        
    class Message(snstype.Message):

        def parse(self):
            self.ID.platform = self.platform

            # For RSS, one entry will be brought up if it is updated. 
            # We use 'update' of RSS as 'created_at' field of SNS stauts. 
            # This is for better message deduplicate

            self.parsed.username = self.raw.get('author')
            # updated is said to be an unsupported field of feedparser
            # in the future versions. 
            self.parsed.created_at = self.raw.get('published')
            self.parsed.title = self.raw.get('title')
            self.parsed.link = self.raw.get('link')

            # Other plugins' statuses have 'text' field
            # The RSS channel is supposed to read contents from
            # different places with different formats. 
            # The entries are usually page update notifications. 
            # We format them in a unified way and use this as 'text'. 
            self.parsed.text = "Article \"%s\" is updated(published)! (%s)" % (self.parsed.title, self.parsed.link)

    def __init__(self, channel = None):
        super(RSS, self).__init__(channel)
        
        self.platform = self.__class__.__name__
        self.Message.platform = self.platform
        
    def read_channel(self, channel):
        super(RSS, self).read_channel(channel)
        
    def auth(self):
        logger.info("%s platform do not need auth!", self.platform)
        
    def home_timeline(self, count=20):
        '''Get home timeline
        get statuses of yours and your friends'
        @param count: number of statuses
        '''

        d = feedparser.parse(self.jsonconf.url)
        
        statuslist = []
        for j in d['items']:
            if len(statuslist) >= count:
                break
            s = self.Message(j)
            #print s.dump_parsed()
            #print s.dump_full()
            #TODO:
            #     RSS parsed result is not json serializable. 
            #     Try to find other ways of serialization. 
            statuslist.append(s)
        return statuslist

class RSS2RW(RSS):

    class Message(RSS.Message):
        def parse(self):
            super(RSS2RW.Message, self).parse()
            self.ID.platform = self.platform

            # RSS2RW channel is intended for snsapi-standardized communication.
            # It does not have to digest RSS entry as is in RSSStatus. 
            # The 'title' field is the place where we put our messages. 
            self.parsed.text = self.parsed.title

    def __init__(self, channel = None):
        super(RSS2RW, self).__init__(channel)

        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

        # default parameter for writing RSS2 feeds
        self.author = "snsapi"
        self.entry_timeout = 3600 #in seconds, default 1 hour

    def read_channel(self, channel):
        super(RSS2RW, self).read_channel(channel)
        if 'author' in channel:
            self.author = channel['author']
        if 'entry_timeout' in channel:
            self.entry_timeout = channel['entry_timeout']

    def update(self, text):
        '''
        Update the RSS2 feeds. 
        The file pointed to by self.jsonconf.url should be writable.
        Remember to set 'author' and 'entry_timeout' in configurations. 
        Or the default values are used. 
        @param text: messages to update in a feeds
        '''

        from dateutil import parser as dtparser, tz

        cur_time = datetime.datetime.now(tz.tzlocal())

        items = []

        # Read and filter existing entries.
        # Old entries are disgarded to keep the file short and clean.
        d = feedparser.parse(self.jsonconf.url)
        for j in d['items']:
            s = self.Message(j)
            #print s
            entry_time = dtparser.parse(s.parsed.created_at)
            if (cur_time - entry_time).seconds < self.entry_timeout:
                items.append( 
                    PyRSS2Gen.RSSItem(
                        author = s.parsed.username, 
                        title = s.parsed.title, 
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
            link = "https://github.com/hupili/snsapi",
            description = "RSS2 R/W channel based on feedparser and PyRSS2Gen",
            lastBuildDate = datetime.datetime.now(),
            items = items
            )

        try:
            rss.write_xml(open(self.jsonconf.url, "w"))
        except:
            raise snserror.op.write

        return True
