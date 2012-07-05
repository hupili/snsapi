# -*- coding: utf-8 -*-

'''
SNS type: status, user, comment
'''

class Status(object):
    def __init__(self, jobj=None):
        self.created_at = ""
        self.id = 0
        self.text = ""
        self.reposts_count = 0
        self.comments_count = 0
        self.user = None
        self.username = ""
        self.usernick = ""
        
        if jobj:
            self.parse(jobj)
            
    def parse(self, jobj):
        pass
    
    
class User(object):
    def __init__(self, jobj=None):
        self.id = 0
        