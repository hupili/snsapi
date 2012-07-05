# -*- coding: utf-8 -*-

import snsapi

class token():
    def __init__(self):
        self.access_token = u''
        

if __name__ == "__main__":
    cli = snsapi.sina.SinaAPI()
    #cli = snsapi.qq.QQAPI()
    #cli.auth()
    t = token()
    cli.token = t
    
    sl = cli.home_timeline()
    for s in sl:
        s.show()