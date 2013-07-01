# -*- coding: utf-8 -*-

from ..snsapi import snstype
from ..snsapi.utils import console_output, console_input
from ..snsapi.snspocket import SNSPocket
from ..snsapi.snslog import SNSLog as logger

sp = SNSPocket()

#This is a github api test file 
# just run. It's as clear as water
#if you want to expand this , go to sns/plugin/github.py 


sp.list_channel()
sp.list_platform()
sp.clear_channel()
nc = sp.new_channel()
nc["platform"] = "GithubStatus"
nc["app_secret"] = "3c5f54512d2a15376f71aeb23c5f2f4b9052be60" #this is my own app secret
nc["app_key"] = "67b3aa1fb2ce9f92d084" #and key
nc["channel_name"] = "test_github"
nc["auth_info"]["client_id"] = "21c4e204de047421728c"
nc["auth_info"]["redirect_uri"] = "http://snsapi.sinaapp.com/auth.php"
sp.add_channel(nc)
sp.auth()
sp[nc['channel_name']].test_show_personnal_info()
sp[nc["channel_name"]].test_show_stars()
sp[nc['channel_name']].test_show_following()
sp.save_config()
sp.list_channel()

	
