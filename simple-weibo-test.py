# -*- coding: utf-8 -*-

import snsapi
from snsapi import snstype
from snsapi.utils import console_output, console_input
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger

sp = SNSPocket()

#This is a much simpler and more clear test file. Hupili's tut file is too complex, and did not provide a `app_secret` and `app_key`

#Don't think too much just run, it will be all clear. ^_^

#xuanqinanhai 2013-1-25 14:43
sp.list_channel()

sp.clear_channel()
nc = sp.new_channel()
nc["platform"] = "SinaWeiboStatus"
nc["app_secret"] = "96bcc1e00268d7e415c32212b3e197fb" #this is my own app secret
nc["app_key"] = "3644324674" #and key
nc["channel_name"] = "test_weibo"
nc["auth_info"]["callback_url"] = "https://snsapi.ie.cuhk.edu.hk/aux/auth.php" #I changed the callback url in my app manage page.
sp.add_channel(nc)
sp.auth()
sp.save_config()
sp.list_channel()

status =  sp.home_timeline()
for each in status:
	print each,
	
