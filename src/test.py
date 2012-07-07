# -*- coding: utf-8 -*-

import snsapi

if __name__ == "__main__":
    cli = snsapi.sina.SinaAPI()
    #cli = snsapi.qq.QQAPI()
    cli.auth()
    sl = cli.home_timeline()
    for s in sl:
        s.show()