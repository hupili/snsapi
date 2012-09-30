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
from ..snsapi import SNSAPI
from .. import snstype
from ..third import feedparser

logger.debug("%s plugged!", __file__)

class RSS(SNSAPI):
        
    class Message(snstype.Status):
        def __get_dict_entry(self, attr, dct, field):
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
            try:
                setattr(self, attr, dct[field])
            except KeyError:
                setattr(self, attr, "(null)")
            
        def parse(self, dct):

            # For RSS, one entry will be brought up if it is updated. 
            # We use 'update' of RSS as 'created_at' field of SNS stauts. 
            # This is for better message deduplicate
            self.__get_dict_entry('username', dct, 'author')
            self.__get_dict_entry('created_at', dct, 'updated')
            self.__get_dict_entry('title', dct, 'title')
            self.__get_dict_entry('link', dct, 'link')

            # Other plugins' statuses have 'text' field
            # The RSS channel is supposed to read contents from
            # different places with different formats. 
            # The entries are usually page update notifications. 
            # We format them in a unified way and use this as 'text'. 
            self.text = "Article \"%s\" is updated(published)! (%s)" % (self.title, self.link)

    def __init__(self, channel = None):
        super(RSS, self).__init__()
        
        self.platform = "rss"
        self.domain = "null"
        
        if channel: 
            self.read_channel(channel)
    
    def read_channel(self, channel):
        self.channel_name = channel['channel_name']
        self.url = channel['url']
        
    def auth(self):
        logger.info("RSS platform do not need auth!")
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
            statuslist.append(self.Message(j))
        return statuslist
