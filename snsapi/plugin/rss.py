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

logger.debug("%s plugged!", __file__)

class RSS(SNSBase):
        
    class Message(snstype.Message):
        def __get_dict_entry(self, dct, field):
            # dict entry reading with fault tolerance. 
            #   self.attr = dct['field']
            # RSS format is very diverse. 
            # To my current knowledge, some format have 
            # 'author' fields, but others do not:
            #    * rss : no
            #    * rss2 : yes
            #    * atom : yes
            #    * rdf : yes
            # This function will return a string "(null)"
            # by default if the field does not exist. 
            # The purpose is to expose unified interface
            # to upper layers. (seeing "(null)" is better 
            # than catching an error. 

            #try:
            #    return dct[field]
            #    #setattr(self, attr, dct[field])
            #except KeyError:
            #    return "(null)"
            #    #setattr(self, attr, "(null)")

            return dict.get(dct, field, "(null)")
            
        def parse(self):
            self.ID.platform = self.platform

            # For RSS, one entry will be brought up if it is updated. 
            # We use 'update' of RSS as 'created_at' field of SNS stauts. 
            # This is for better message deduplicate

            #self.parsed.username = self.__get_dict_entry(dct, 'author')
            #self.parsed.created_at = self.__get_dict_entry(dct, 'updated')
            #self.parsed.title = self.__get_dict_entry(dct, 'title')
            #self.parsed.link = self.__get_dict_entry(dct, 'link')

            self.parsed.username = self.raw.get('author')
            self.parsed.created_at = self.raw.get('updated')
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
        logger.info("RSS platform do not need auth!")
        
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
