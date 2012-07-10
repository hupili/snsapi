# -*- coding: utf-8 -*-

import snsapi

if __name__ == "__main__":
    cli = snsapi.rss.RSSAPI()
    #cli = snsapi.sina.SinaAPI()
    #cli = snsapi.qq.QQAPI()
    cli.auth()
    #cli.get_saved_token()
    sl = cli.home_timeline()
    for s in sl:
        s.show()
