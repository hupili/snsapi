from snscli import *
import snsapi
from snsapi.plugin_trial import Email
from snsapi import snstype
from snsapi.utils import console_output, console_input
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger
import quopri
import time
import email
from email.mime.text import MIMEText
from email.header import decode_header, make_header
import imaplib
import smtplib

import base64
import re


nc=new_channel()
nc['platform']="RenrenFeed"
nc['app_secret']="1db5c5bf4ca44a75b3e6065f401d0b16"
nc['app_key']="268874"
nc["channel_name"]="test_renren"
nc["auth_info"]["callback_url"]="http://snsapi.sinaapp.com/auth.php"
add_channel(nc)

#nc1=new_channel(full=True)
#nc1['platform']="TwitterStatus"
#nc1['app_secret']="xOl31NQFrO9mn99tvvf5wmYBjeJT2V50gJNrPNHs6c"
#nc1['app_key']="jNeenbpkNvGnGgR09AbXRQ"
#nc1["channel_name"]="test_twitter"
#nc1['access_key'] = '1599990409-keJcjxyibqjHkEdEeZ1LkvcIiw809I0N9HCvRRH'
#nc1['access_secret'] = '4fk0WmEos6bTEMuA7cjYAjGNkmLqusQAzAkrbFgq3M'
#add_channel(nc1)
#
#nc2 = Email.new_channel()
#nc2['platform']="Email"
#nc2["channel_name"]="test_126email"
#nc2['username']="mua11zx.xh"
#nc2['password']="52Luneng"
#nc2['address']="mua11zx.xh@gmail.com"
#nc2['imap_host'] = 'imap.gmail.com'
#nc2['imap_port'] = 993 #default IMAP + TLS port
#nc2['smtp_host'] = 'smtp.gmail.com'
#nc2['smtp_port'] = 587 #default SMTP + TLS port
##
##add_channel(nc2)
#sp = SNSPocket()
#sp.list_channel()
#sp.clear_channel()
#x = Email()
#nc3 = Email.new_channel()
##nc3['platform']="Email"
#nc3["channel_name"]="test_email"
#nc3['username']="wcyz666@126.com"
#nc3['password']="203039IamWC"
#nc3['address']="wcyz666@126.com"
#nc3['imap_host'] = 'imap.126.com'
#nc3['imap_port'] = 993 #default IMAP + TLS port
#nc3['smtp_host'] = 'smtp.126.com'
#nc3['smtp_port'] = 25 #default SMTP + TLS port
#text="www"
#msg = MIMEText(text, _charset = 'utf-8')
#x.read_channel(nc2)
#x.auth()
#x.add_buddy(address = "mua11zx.xh@gmail.com")
##x._send_to_all_buddy("aaiaa", msg)
#x.add_buddy(address = "wcyz666@126.com")
#x.update("Hello world!", title="hello")
#
#
##
#
#nc4 = new_channel()
#nc4['platform']="FacebookFeed"
#nc4["channel_name"]="test_fb"
#nc4["access_token"]="CAAClpCoLrVQBAN9h2FdCROdzHAIZCAWGOj1m1mCBSgo4It6MZCeZA4tuo6FunA6i99fGehZB6fCKkMjE6jkTfVsoDBdv9DwxfpMLAQWr9jaj1wAwjPg0u25DRqkZCUOKRKW9gZCDaZAfUwEGzDN6f0ATmVl9MbmoV4OFCTfXeEzrXW0fjOw23p2vh6dZCTaqxZCUZD"
#nc4["app_key"]="182124498627924"
#nc4["app_secret"]="6b16d0cf4fa25f6bbc63624d3059a77f"
#nc4["auth_info"]["callback_url"]= "http://snsapi.ie.cuhk.edu.hk/aux/auth.php"
#add_channel(nc4)
auth()
sl = home_timeline(count = 5)
for i in sl:
    print(like(i))
#print sl

