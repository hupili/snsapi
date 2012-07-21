# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''
import utils
import errors

class Status(object):
    def __init__(self, dct=None):
        self.created_at = ""
        self.id = 0
        self.text = ""
        self.reposts_count = 0
        self.comments_count = 0
        self.user = None
        self.username = ""
        self.usernick = ""
        
        try:
            self.parse(dct)
        except AttributeError:
            raise errors.snsTypeParseError
            
    def parse(self, dct):
        pass
    
    
class User(object):
    def __init__(self, jobj=None):
        self.id = 0
        
class Error(dict):
    def show(self):
        print self

class AuthenticationInfo:
    #default auth configurations
    def __init__(self, auth_info = None):
        if auth_info :
            self.callback_url = auth_info['callback_url']
            self.cmd_fetch_code = auth_info['cmd_fetch_code']
            self.cmd_request_url = auth_info['cmd_request_url'] 
            self.save_token_file = auth_info['save_token_file'] 
        else :
            self.callback_url = None
            self.cmd_fetch_code = "(built-in)"
            self.cmd_request_url = "(built-in)"
            self.save_token_file = "(built-in)"

if __name__ == "__main__":
    s = Status("fe")
    s.show()
