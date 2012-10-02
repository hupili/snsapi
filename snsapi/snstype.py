# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''
import utils
from errors import snserror
from snsconf import SNSConf

class MessageID(utils.JsonDict):
    """
    All information to locate one status is here. 

    It shuold be complete so that:

       * one can invoke reply() function of plugin on this object. 
       * Or one can invoke reply() function of container on this object. 

    In order to reply one status, here's the information 
    required by each platforms:

       * Renren: the status_id and source_user_id
       * Sina: status_id
       * QQ: status_id

    """
    def __init__(self, platform = None, status_id = None, source_user_id = None):
        super(MessageID, self).__init__()

        self.platform = platform
        self.status_id = status_id
        self.source_user_id = source_user_id

    def __str__(self):
        """docstring for __str__"""
        return "(p:%s|sid:%s|uid:%s)" % \
                (self.platform, self.status_id, self.source_user_id)
        

class Message(utils.JsonDict):
    def __init__(self, dct=None):
        #self.created_at = ""
        #self.id = 0
        #self.text = ""
        #self.reposts_count = 0
        #self.comments_count = 0
        #self.user = None
        #self.username = ""
        #self.usernick = ""

        if dct:
            self['raw'] = utils.JsonDict(dct)
        else:
            self['raw'] = utils.JsonDict({})
        self['parsed'] = utils.JsonDict({})

        self['ID'] = MessageID()
        
        try:
            self.parse(dct)
        #except AttributeError:
        except KeyError, e:
            raise snserror.type.parse(e.message)
            
    def parse(self, dct):
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
                (self.parsed.username, self.parsed.created_at, self.parsed.text)

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


class MessageList(list):
    """
    A list of Message object 
    """
    def __init__(self):
        super(MessageList, self).__init__()

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
            #self.callback_url = auth_info['callback_url']
            #self.cmd_fetch_code = auth_info['cmd_fetch_code']
            #self.cmd_request_url = auth_info['cmd_request_url'] 
            #self.save_token_file = auth_info['save_token_file'] 
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
    s.show()
