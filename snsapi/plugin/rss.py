#-*- encoding: utf-8 -*-

'''
RSS Feed 

Contains:
   * RSS Read-only feed platform. 
   * RSS Read/Write platform.

'''


from ..snslog import SNSLog as logger 
from ..snsbase import SNSBase
from .. import snstype
from ..third import feedparser
import datetime
from ..third import PyRSS2Gen
from ..errors import snserror
from .. import utils

logger.debug("%s plugged!", __file__)

class RSSMessage(snstype.Message):
    platform = "RSS"

    def parse(self):
        self.ID.platform = self.platform

        self.parsed.username = self.raw.get('author')
        #TODO:
        #    According to the notion of ID, it should identify 
        #    a single user in a cross platform fashion. From the 
        #    message, we know platform is RSS. However, author 
        #    name is not enough. Suppose all feeds do their due
        #    dilligence to make 'author' identifiable, we can 
        #    use 'url' (of RSS feed) + 'author' to identify a 
        #    single user of RSS platform. This requires some 
        #    framework change in SNSAPI, allowing putting this 
        #    prefix information to Message class (not Message 
        #    instance). 
        self.parsed.userid = self.raw.get('author')
        self.parsed.time = utils.str2utc(self.raw.get(['updated', 'published']))

        self.parsed.title = self.raw.get('title')
        self.parsed.link = self.raw.get('link')

        # Other plugins' statuses have 'text' field
        # The RSS channel is supposed to read contents from
        # different places with different formats. 
        # The entries are usually page update notifications. 
        # We format them in a unified way and use this as 'text'. 
        self.parsed.text = "Article \"%s\" is updated(published)! (%s)" % (self.parsed.title, self.parsed.link)

class RSS(SNSBase):
    '''
    Supported Methods
        * auth() : 
            a NULL stub. 
        * home_timeline() : 
            read and parse RSS feed.
            pretend it to be a 'special' SNS platform, 
            where you can only read your wall but can 
            not write to it.
    '''

    Message = RSSMessage

    def __init__(self, channel = None):
        super(RSS, self).__init__(channel)
        self.platform = self.__class__.__name__

    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)
        c['platform'] = 'RSS'
        c['url'] = 'https://github.com/hupili/snsapi/commits/master.atom'

        return c
        
    def read_channel(self, channel):
        super(RSS, self).read_channel(channel)

    def auth(self):
        logger.info("%s platform do not need auth!", self.platform)
        
    def auth_first(self):
        logger.info("%s platform do not need auth_first!", self.platform)

    def auth_second(self):
        logger.info("%s platform do not need auth_second!", self.platform)

    def home_timeline(self, count=20):
        '''Get home timeline

           * function : get statuses of yours and your friends'
           * parameter count: number of statuses
        '''

        d = feedparser.parsetere(self.jsonconf.url)
        
        statuslist = snstype.MessageList()
        for j in d['items']:
            if len(statuslist) >= count:
                break
            s = self.Message(j,\
                    platform = self.jsonconf['platform'],\
                    channel = self.jsonconf['channel_name']\
                    )
            #print s.dump_parsed()
            #print s.dump_full()
            #TODO:
            #     RSS parsed result is not json serializable. 
            #     Try to find other ways of serialization. 
            statuslist.append(s)
        return statuslist

    def expire_after(self, token = None):
        # This platform does not have token expire issue. 
        return -1

class RSS2RWMessage(RSSMessage):
    platform = "RSS2RW"
    def parse(self):
        super(RSS2RWMessage, self).parse()
        self.ID.platform = self.platform

        # RSS2RW channel is intended for snsapi-standardized communication.
        # It does not have to digest RSS entry as is in RSSStatus. 
        # The 'title' field is the place where we put our messages. 
        self.parsed.text = self.parsed.title

class RSS2RW(RSS):
    '''
    Read/Write Channel for rss2

    '''

    Message = RSS2RWMessage

    def __init__(self, channel = None):
        super(RSS2RW, self).__init__(channel)

        self.platform = self.__class__.__name__

        # default parameter for writing RSS2 feeds
        self.author = "snsapi"
        self.entry_timeout = 3600 #in seconds, default 1 hour

    @staticmethod
    def new_channel(full = False):
        c = RSS.new_channel(full)
        c['platform'] = 'RSS2RW'
        return c

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
        
           * parameter text: messages to update in a feeds
        '''

        from dateutil import parser as dtparser, tz

        #cur_time = datetime.datetime.now(tz.tzlocal())
        cur_time = self.time()

        items = []

        # Read and filter existing entries.
        # Old entries are disgarded to keep the file short and clean.
        d = feedparser.parse(self.jsonconf.url)
        for j in d['items']:
            s = self.Message(j)
            #print s
            #entry_time = dtparser.parse(s.parsed.time)
            #entry_time = datetime.datetime.utcfromtimestamp(s.parsed.time)
            entry_time = s.parsed.time
            if cur_time - entry_time < self.entry_timeout:
                items.append( 
                    PyRSS2Gen.RSSItem(
                        author = s.parsed.username, 
                        title = s.parsed.title, 
                        description = "snsapi RSS2RW update",
                        pubDate = utils.utc2str(entry_time)
                        )
                    )

        items.insert(0, 
            PyRSS2Gen.RSSItem(
                author = self.author, 
                title = text, 
                description = "snsapi RSS2RW update",
                pubDate = utils.utc2str(cur_time)
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
        except Exception, e:
            raise snserror.op.write(e.message)

        return True
