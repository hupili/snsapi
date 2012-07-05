# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''

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
        
        if dct:
            self.parse(dct)
            
    def parse(self, dct):
        pass
    
    
class User(object):
    def __init__(self, jobj=None):
        self.id = 0
        