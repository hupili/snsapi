#-*- encoding: utf-8 -*-

'''
QQ micro-blog client
'''

from ..snsapi import SNSAPI
print "QQ weibo plugged!"

class QQAPI(SNSAPI):
    def __init__(self):
        super(QQAPI, self).__init__()
        self.app_key = ""
        self.app_secret = ""

    def auth(self):
        auth_url = "https://open.t.qq.com/cgi-bin/oauth2/"
        callback_url = "http://copy.the.code.to.client/"
        self.oauth2(auth_url, callback_url)