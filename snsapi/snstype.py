# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''

import hashlib

import utils
from errors import snserror
from snsconf import SNSConf
from snslog import SNSLog as logger

class MessageID(utils.JsonDict):
    """
    All information to locate one status is here. 

    It shuold be complete so that:

       * one can invoke reply() function of plugin on this object. 
       * Or one can invoke reply() function of container on this object. 

    There are two mandatory fields:

       * platform: Name of the platform (e.g. RenrenStatus)
       * channel: Name of the instantiated channel \
       (e.g. 'renren_account_1'). \
       Same as a channel's ``.jsonconf['channel_name']``.

    In order to reply one status, here's the information 
    required by each platforms:

       * Renren: the status_id and source_user_id
       * Sina: status_id
       * QQ: status_id

    """
    #def __init__(self, platform = None, status_id = None, source_user_id = None):
    def __init__(self, platform = None, channel = None):
        super(MessageID, self).__init__()

        self.platform = platform
        self.channel = channel
        #self.status_id = status_id
        #self.source_user_id = source_user_id

    #def __str__(self):
    #    """docstring for __str__"""
    #    return "(p:%s|sid:%s|uid:%s)" % \
    #            (self.platform, self.status_id, self.source_user_id)
    
    def __str__(self):
        return self._dumps()


class Message(utils.JsonDict):
    '''
    The Message base class for SNSAPI

    Data Fields:

       * 'platform': a string describing the platform\
       where this message come from. See 'snsapi/platform.py'\
       for more details.
       * 'raw': the raw json or XML object returned from\
       the platform spefiic API. This member is here to give\
       upper layer developers the last chance of manipulating\
       any available information. Having an understanding of\
       the platform-specific returning format is esential.
       * 'parsed': this member abstracts some common fields\
       that all messages are supposed to have. e.g. 'username',\
       'time', 'text', etc.
       * 'ID': a MessageID object. This ID should be enough\
       to indentify a message across all different platforms.

    For details of 'ID', please see the docstring of MessageID().

    Mandatory fields of 'parsed' are:

       * time: a utc integer. (some platform returns parsed string)
       * userid: a string. (called as "username" at some platform)
       * username: a string. (called as "usernick" as some platform)
       * text: a string. (can be 'text' in the returning json object,\
       or parsed from other fields.)

    Optional fields of 'parsed' are:

       * reposts_count: an integer. For some OSN.
       * comments_count: an integer. For some OSN.
       * link: a string. For RSS; Parsed from microblog message;\
       Parsed from email message; etc.
       * title: a string. For RSS; Blog channel of some OSN.
       * description: a string. For RSS digest text;\
       Sharing channel of some OSN; etc.
       * text_orig: a string. The original text, also known as\
       "root message" in some context. e.g. the earliest status\
       in one thread.
       * text_last: a string. The latest text, also known as\
       "message" in some context. e.g. the reply or forwarding\
       comments made by the last user.
       * text_trace: a string. Using any (can be platform-specific)\
       method to construt the trace of this message. e.g.\
       the forwarding / retweeting / reposting sequence.\
       There is no unified format yet.
       * username_origin: a string. The username who posts 'text_orig'.

    '''

    platform = "SNSAPI"

    def __init__(self, dct = None, platform = None, channel = None):
        
        self['deleted'] = False
        self['ID'] = MessageID(platform, channel)
        #if platform:
        #    self['ID']['platform'] = platform
        #if channel:
        #    self['ID']['channel'] = channel

        self['raw'] = utils.JsonDict({})
        self['parsed'] = utils.JsonDict({})
        if dct:
            self['raw'] = utils.JsonDict(dct)
            try:
                self.parse()
            except KeyError, e:
                raise snserror.type.parse(e.message)
        
    def parse(self):
        '''
        Parse self.raw and store result in self.parsed

        '''
        pass

    def show(self):
        '''
        Level 1 serialization and print to console

        See dump()

        '''
        utils.console_output(unicode(self))
    
    def __str__(self):
        '''
        Level 1 serialization and convert to str using console encoding

        See dump()

        '''
        return unicode(self).encode(SNSConf.SNSAPI_CONSOLE_STDOUT_ENCODING)

    def __unicode__(self):
        '''
        Level 1 serialization and convert to unicode

        See dump()

        '''
        return self.dump()

    def dump(self):
        '''
        Level 1 serialization: console output. 

        This level targets console output. It only digests essnetial 
        information which end users can understand. e.g. the text
        of a status is digested whereas the ID fields is not digested. 

        To control the format, please rewrite dump() in derived Message class. 

        See also __str__(), __unicode__(), show()

        '''
        return unicode("[%s] at %s \n  %s") % \
                (self.parsed.username, utils.utc2str(self.parsed.time), self.parsed.text)

    def dump_parsed(self):
        '''
        Level 2 serialization: interface output. 

        This level targets both Python class interface and
        STDIO/STDOUT interface. The output of all kinds of 
        Messages conform to the same format. The json object
        can be used to pass information in/out SNSAPI using 
        Python class. It is also able to pretty print, so 
        that the STDOUT result is easy to parse in any 
        language. 
        '''
        return self.parsed._dumps_pretty()


    def dump_full(self):
        '''
        Level 3 serialization: complete output. 

        This level targets more sophisticated applications. 
        The basic function of SNSAPI is to unify different 
        formats. That's what the first two level of 
        serialization do. However, app developers may want 
        more sophisticated processing. We serialize the full 
        Message object through this function. In this way, 
        app developers can get all information they need. 
        Note that knowledge of the platform specific return 
        format is essential. We conclude their fields in:

           * https://github.com/hupili/snsapi/wiki/Status-Attributes
        
        This wiki page may not always be up to date. Please
        refer to the offical API webpage for more info. 
        '''
        return self._dumps()

    def digest(self):
        '''
        Digest the message content. This value is useful in 
        for example forwarding services to auto-reply services, 
        for those applications requires message deduplication.

        It corresponds to dump(). 

        Note: different messages may be regarded as the same 
        according to this digest function. 

        '''
        return hashlib.sha1(self.dump().encode('utf-8')).hexdigest()

    def digest_parsed(self):
        '''
        It corresponds to dump_parsed()

        '''
        return hashlib.sha1(self.dump_parsed().encode('utf-8')).hexdigest()

    def digest_full(self):
        '''
        It corresponds to dump_full()

        '''
        return hashlib.sha1(self.dump_full().encode('utf-8')).hexdigest()

#class DeletedMessage(Message):
#    """docstring for DeletedMessage"""
#    def __init__(self, dct):
#        super(DeletedMessage, self).__init__(dct, "deleted", "deleted")
        

class MessageList(list):
    """
    A list of Message object 
    """
    def __init__(self):
        super(MessageList, self).__init__()

    def append(self, e):
        if isinstance(e, Message):
            if hasattr(e, 'deleted') and e.deleted:
                logger.debug("Trying to append Deleted Message type element. Ignored")
            else:
                super(MessageList, self).append(e)
        else:
            logger.debug("Trying to append non- Message type element. Ignored")

    def extend(self, l):
        if isinstance(l, MessageList):
            super(MessageList, self).extend(l)
        elif isinstance(l, list):
            # We still extend the list if the user asks to. 
            # However, a warning will be placed. Doing this 
            # may violate some properties of MessageList, e.g. 
            # there is no Deleted Message in the list. 
            super(MessageList, self).extend(l)
            logger.warning("Extend MessageList with non MessageList list.")
        else:
            logger.warning("Extend MessageList with unknown type.")

    def __str__(self):
        tmp = ""
        no = 0 
        for s in self:
            tmp = tmp + "<%d>\n%s\n" % (no, str(s))
            no = no + 1
        return tmp

    def __unicode__(self):
        tmp = ""
        no = 0 
        for s in self:
            tmp = tmp + "<%d>\n%s\n" % (no, unicode(s))
            no = no + 1
        return tmp
        
class User(object):
    def __init__(self, jobj=None):
        self.id = 0
        
class AuthenticationInfo(utils.JsonObject):
    #default auth configurations
    def __init__(self, auth_info = None):
        if auth_info :
            self.update(auth_info)
        else :
            self.callback_url = None
            self.cmd_fetch_code = "(default)"
            self.cmd_request_url = "(default)"
            self.save_token_file = "(default)"

    def set_defaults(self):
        DEFAULT_MAPPING = {
                "cmd_request_url": "(local_webserver)+(webbrowser)",
                "cmd_fetch_code": "(local_webserver)"
                }
        for (k,v) in DEFAULT_MAPPING.items():
            if (not (k in self)) or (self[k] == "(default)"):
                self[k] = DEFAULT_MAPPING[k]

if __name__ == "__main__":
    s = Message({"text":"fe啊"})
    #s.show()
