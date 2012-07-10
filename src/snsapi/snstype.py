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
        
        if type(dct) == dict:
            try:
                self.parse(dct)
            except AttributeError:
                raise errors.snsTypeParseError
        else:
            raise errors.snsTypeWrongInput(dct)
            
    def parse(self, dct):
        pass
    
    
class User(object):
    def __init__(self, jobj=None):
        self.id = 0

if __name__ == "__main__":
    s = Status("fe")
    s.show()
