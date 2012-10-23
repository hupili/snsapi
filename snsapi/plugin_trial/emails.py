#-*- encoding: utf-8 -*-

'''
email platform

Support get message by IMAP and send message by SMTP

The file is named as "emails.py" instead of "email.py"
because there is a package in Python called "email". 
We will import that package..

'''

import email
import imaplib
import smtplib

#def extract_body(payload):
#    if isinstance(payload,str):
#        return payload
#    else:
#        return '\n'.join([extract_body(part.get_payload()) for part in payload])
#
#conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
#
#conn.login(,)
##fail, imap.error, find substring AUTHENTICATIONFAILED
#
#conn.select()
#typ, data = conn.search(None, 'ALL')
#try:
#    for num in data[0].split():
#        typ, msg_data = conn.fetch(num, '(RFC822)')
#        for response_part in msg_data:
#            if isinstance(response_part, tuple):
#                msg = email.message_from_string(response_part[1])
#                #subject=msg['subject']                   
#                ##print msg
#                #print(subject)
#                print msg['From']
#                print msg['To']
#                print msg['Subject']
#                print msg['Date']
#                print msg['Content-Type']
#                #payload=msg.get_payload()
#                #body=extract_body(payload)
#                #print(body)
#        #typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
#finally:
#    try:
#        conn.close()
#    except:
#        pass
#    conn.logout()


#fromaddr = 'hupili.snsapi@gmail.com'  
##toaddrs  = 'hupili.snsapi@gmail.com, hpl1989@gmail.com'  
#toaddrs  = 'hpl1989@gmail.com'  
##msg = "" 
##msg += "Subject: test\n"
##msg += "Date: Oct 23 2012\n"
##msg += 'a test message from snsapi'  
#
#from email.mime.text import MIMEText
##msg = email.mime.text.MIMEText("body...")
##msg = MIMEText("body...")
#msg = MIMEText(u'测试中文', _charset = 'utf-8')
##msg = MIMEText()
#msg['From'] = fromaddr
#msg['To'] = toaddrs
#msg['Subject'] = 'test'
##msg.set_payload(u'测试中文')
#
## The actual mail send  
#server = smtplib.SMTP('smtp.gmail.com:587')  
#server.starttls()  
##server.login(username,password)  
#server.login(,)
#server.sendmail(fromaddr, toaddrs, msg.as_string())  
#server.quit()  


# === email message fields for future reference
# TODO:
#     Enhance the security level by check fields like 
#     'Received'. GMail has its checking at the web 
#     interface side. Fraud identity problem will be 
#     alleviated. 
# In [7]: msg.keys()
# Out[7]: 
# ['Delivered-To',
# 'Received',
# 'Received',
# 'Return-Path',
# 'Received',
# 'Received-SPF',
# 'Authentication-Results',
# 'Received',
# 'DKIM-Signature',
# 'MIME-Version',
# 'Received',
# 'X-Notifications',
# 'X-UB',
# 'X-All-Senders-In-Circles',
# 'Date',
# 'Message-ID',
# 'Subject',
# 'From',
# 'To',
# 'Content-Type']
# 
# In [8]: msg['From']
# Out[8]: '"Google+ team" <noreply-daa26fef@plus.google.com>'
# 
# In [9]: msg['To']
# Out[9]: 'hupili.snsapi@gmail.com'
# 
# In [10]: msg['Subject']
# Out[10]: 'Getting started on Google+'
# 
# In [11]: msg['Date']
# Out[11]: 'Mon, 22 Oct 2012 22:37:37 -0700 (PDT)'
# 
# In [12]: msg['Content-Type']
# Out[12]: 'multipart/alternative; boundary=047d7b5dbe702bc3f804ccb35e18'
