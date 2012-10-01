# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''
import utils
from errors import snserror
from snsconf import SNSConf

class MessageID(object):
    """
    All information to locate one status is here. 

    It shuold be complete so that:

       * one can invoke reply() function of plugin on this object. 
       * Or one can invoke reply() function of container on this object. 

    In order to reply one status, here's the information 
    required by each platforms:

       * Renren: the status_id and source_user_id
       * Sina:
       * QQ:

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
        

class Message(object):
    def __init__(self, dct=None):
        self.created_at = ""
        self.id = 0
        self.text = ""
        self.reposts_count = 0
        self.comments_count = 0
        self.user = None
        self.username = ""
        self.usernick = ""

        self.ID = MessageID()
        
        try:
            self.parse(dct)
        #except AttributeError:
        except KeyError:
            raise snserror.type.parse
            
    def parse(self, dct):
        pass

    def show(self):
        utils.console_output(unicode(self))
    
    def __str__(self):
        return unicode(self).encode(SNSConf.SNSAPI_CONSOLE_STDOUT_ENCODING)

    def __unicode__(self):
        return "[%s] at %s \n  %s" % \
                (self.username, self.created_at, self.text)

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
        for s in self:
            tmp = tmp + unicode(s) + "\n"
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
    s = Message("fe")
    s.show()
