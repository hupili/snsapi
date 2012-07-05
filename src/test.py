#!/usr/bin/env python
# -*- coding: utf-8 -*-

import snsapi

if __name__ == "__main__":
    #cli = snsapi.sina.SinaAPI()
    cli = snsapi.qq.QQAPI()
    cli.auth()