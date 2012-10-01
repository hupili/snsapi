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
from rss import RSS
from ..third import feedparser
from ..third import PyRSS2Gen
from ..errors import snserror

logger.debug("%s plugged!", __file__)

class RSS2RW(RSS):

    class Message(RSS.Message):
        def parse(self, dct):
            super(RSS2RW.Message, self).parse(dct)
            self.ID.platform = self.platform

            # RSS2RW channel is intended for snsapi-standardized communication.
            # It does not have to digest RSS entry as is in RSSStatus. 
            # The 'title' field is the place where we put our messages. 
            self.text = self.title

    def __init__(self, channel = None):
        super(RSS2RW, self).__init__(channel)


        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

        #default parameter for writing RSS2 feeds
        self.author = "snsapi"
        self.entry_timeout = 3600 #in seconds, default 1 hour

        #if channel: 
        #    self.read_channel(channel)

    def read_channel(self, channel):
        super(RSS2RW, self).read_channel(channel)
        if 'author' in channel:
            self.author = channel['author']
        if 'entry_timeout' in channel:
            self.entry_timeout = channel['entry_timeout']

    def auth(self):
        logger.info("RSS2RW platform do not need auth!")
        return 

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
            statuslist.append(self.Message(j))
        return statuslist

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

        #Read and filter existing entries.
        #Old entries are disgarded to keep the file short and clean.
        d = feedparser.parse(self.jsonconf.url)
        for j in d['items']:
            s = self.Message(j)
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
