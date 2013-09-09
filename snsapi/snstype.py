# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''

import hashlib

import utils
from errors import snserror
from snsconf import SNSConf
from snslog import SNSLog as logger


class BooleanWrappedData:
    def __init__(self, boolval, data=None):
        self.boolval = boolval
        self.data = data

    def __nonzero__(self):
        return self.boolval

    def __eq__(self, other):
        if self.boolval ^ bool(other):
            return False
        else:
            return True

    def __unicode__(self):
        return unicode((self.boolval, self.data))

    def __str__(self):
        return str((self.boolval, self.data))

    def __repr__(self):
        return repr((self.boolval, self.data))

class MessageID(utils.JsonDict):
    """
    All information to locate one status is here.

    It shuold be complete so that:

       * one can invoke reply() function of plugin on this object.
       * Or one can invoke reply() function of container on this object.

    There are two mandatory fields:

       * platform: Name of the platform (e.g. RenrenStatus)
       * channel: Name of the instantiated channel
         (e.g. 'renren_account_1').
         Same as a channel's ``.jsonconf['channel_name']``.

    In order to reply one status, here's the information
    required by each platforms:

       * Renren: the status_id and source_user_id
       * Sina: status_id
       * QQ: status_id

    **NOTE**: This object is mainly for SNSAPI to identify a Message.
    Upper layer had better not to reference fields of this object directly.
    If you must reference this object, please do not touch those
    non-mandatory fields.

    """
    def __init__(self, platform = None, channel = None):
        super(MessageID, self).__init__()

        self.platform = platform
        self.channel = channel

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

       * ``platform``: a string describing the platform
         where this message come from. See 'snsapi/platform.py'
         for more details.
       * ``raw``: the raw json or XML object returned from
         the platform spefiic API. This member is here to give
         upper layer developers the last chance of manipulating
         any available information. Having an understanding of
         the platform-specific returning format is esential.
       * ``parsed``: this member abstracts some common fields
         that all messages are supposed to have. e.g. 'username',
         'time', 'text', etc.
       * ``ID``: a ``MessageID`` object. This ID should be enough
         to indentify a message across all different platforms.

    For details of ``ID``, please see the docstring of ``MessageID``.

    Mandatory fields of ``parsed`` are:

       * ``time:`` a utc integer. (some platform returns parsed string)
       * ``userid:`` a string. (called as "username" at some platform)
       * ``username:`` a string. (called as "usernick" as some platform)
       * ``text:`` a string. (can be 'text' in the returning json object,
         or parsed from other fields.)
       * ``attachments``: an array of attachments. Each attachment is:
         ``{'type': TYPE, 'format': [FORMAT1, FORMAT2, ...], 'data': DATA}``.
         TYPE can be one of ``link``, ``picture``, ``album``, ``video``, ``blog``.
         FORMAT can be ``link``, ``binary``, ``text`` and ``other``.
         DATA is your data presented in FORMAT.

    Optional fields of 'parsed' are:

       * ``deleted``: Bool. For some OSN.
       * ``reposts_count``: an integer. For some OSN.
       * ``comments_count``: an integer. For some OSN.
       * ``link``: a string. For RSS; Parsed from microblog message;
         Parsed from email message; etc.
       * ``title``: a string. For RSS; Blog channel of some OSN.
       * ``description``: a string. For RSS digest text;
         Sharing channel of some OSN; etc.
       * ``body``: a string. The 'content' of RSS, the 'body' of HTML,
         or whatever sematically meaning the body of a document.
       * ``text_orig``: a string. The original text, also known as
         "root message" in some context. e.g. the earliest status
         in one thread.
       * ``text_last``: a string. The latest text, also known as
         "message" in some context. e.g. the reply or forwarding
         comments made by the last user.
       * ``text_trace``: a string. Using any (can be platform-specific)
         method to construt the trace of this message. e.g.
         the forwarding / retweeting / reposting sequence.
         There is no unified format yet.
       * ``username_origin``: a string. The username who posts 'text_orig'.

    '''

    platform = "SNSAPI"

    def __init__(self, dct = None, platform = None, channel = None, conf = {}):

        self.conf = conf
        self['deleted'] = False
        self['ID'] = MessageID(platform, channel)

        self['raw'] = utils.JsonDict({})
        self['parsed'] = utils.JsonDict({'attachments' : []})
        if dct:
            self['raw'] = utils.JsonDict(dct)
            try:
                self.parse()
            except KeyError as e:
                raise snserror.type.parse(str(e))

    def parse(self):
        '''
        Parse self.raw and store result in self.parsed

        '''
        # Default action: copy all fields in 'raw' to 'parsed'.
        self.parsed.update(self.raw)

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
        # NOTE:
        #
        #     dump() method remains stable because the downstream is
        #     digest methods. The __str__ and __unicode__ are only
        #     for console interaction. Normal apps should refer to
        #     those fields in 'parsed' themselves.
        #
        #     We limit the output to 500 characters to make the console
        #     output uncluttered.
        return unicode("[%s] at %s \n  %s") % (self.parsed.username,
                utils.utc2str(self.parsed.time),
                self.parsed.text[0:500])

    def dump(self, tz=None):
        '''
        Level 1 serialization: console output.

        This level targets console output. It only digests essnetial
        information which end users can understand. e.g. the text
        of a status is digested whereas the ID fields is not digested.

        To control the format, please rewrite dump() in derived Message class.

        See also __str__(), __unicode__(), show()

        '''
        if tz:
            return unicode("[%s] at %s \n  %s") % \
                    (self.parsed.username, utils.utc2str(self.parsed.time, tz), self.parsed.text)
        else:
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
        from utils import FixedOffsetTimeZone
        tz = FixedOffsetTimeZone(0, 'GMT')
        return hashlib.sha1(self.dump(tz=tz).encode('utf-8')).hexdigest()

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


class MessageList(list):
    """
    A list of Message object
    """
    def __init__(self, init_list=None):
        super(MessageList, self).__init__()
        if init_list:
            self.extend(init_list)

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
    # default auth configurations
    def __init__(self, auth_info = None):
        if auth_info :
            self.update(auth_info)
        else :
            self.callback_url = None
            self.cmd_fetch_code = "(default)"
            self.cmd_request_url = "(default)"
            self.save_token_file = "(default)"
            self.login_username = None
            self.login_password = None

    def set_defaults(self):
        DEFAULT_MAPPING = {
                "cmd_request_url": "(local_webserver)+(webbrowser)",
                "cmd_fetch_code": "(local_webserver)"
                }
        for (k,v) in DEFAULT_MAPPING.items():
            if (not (k in self)) or (self[k] == "(default)"):
                self[k] = DEFAULT_MAPPING[k]

if __name__ == "__main__":
    import time
    m1 = Message({'text': 'test',
        'username': 'snsapi',
        'userid': 'snsapi',
        'time': time.time() })
    m2 = Message({'text': u'测试',
        'username': 'snsapi',
        'userid': 'snsapi',
        'time': time.time() })
    ml = MessageList()
    ml.append(m1)
    ml.append(m2)
    # NOTE:
    #     When you develop new plugins, the MessageList returned
    #     by your ``home_timeline`` should be printable in this
    #     way. This is minimum checking for whether you have
    #     mandatory fields.
    print ml
