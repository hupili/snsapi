#-*- encoding: utf-8 -*-

'''
email platform

Support get message by IMAP and send message by SMTP

The file is named as "emails.py" instead of "email.py"
because there is a package in Python called "email". 
We will import that package..

'''

from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype
from ..utils import console_output
from .. import utils

import email
import imaplib
import smtplib

logger.debug("%s plugged!", __file__)

class Email(SNSBase):
    class Message(snstype.Message):
        def parse(self):
            self.ID.platform = self.platform
            self._parse(self.raw)

        def _parse(self, dct):
            self.parsed.title = dct.get('Subject')
            self.parsed.text = dct.get('Subject')
            self.parsed.time = utils.str2utc(dct.get('Date'))
            self.parsed.username = dct.get('From')
            self.parsed.userid = dct.get('From')

    def __init__(self, channel = None):
        super(Email, self).__init__(channel)

        self.platform = self.__class__.__name__
        self.Message.platform = self.platform

        self.imap = None
        self.smtp = None

    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'Email'
        c['imap_host'] = 'imap.gmail.com'
        c['imap_port'] = 993 #default IMAP + TLS port
        c['smtp_host'] = 'smtp.gmail.com'
        c['smtp_port'] = 587 #default SMTP + TLS port 
        c['username'] = 'username'
        c['password'] = 'password'
        c['address'] = 'username@gmail.com'
        return c
        
    def read_channel(self, channel):
        super(Email, self).read_channel(channel) 

    def _extract_body(self, payload):
        #TODO:
        #    Extract and decode if necessary. 
        if isinstance(payload,str):
            return payload
        else:
            return '\n'.join([self._extract_body(part.get_payload()) for part in payload])
    
    def _receive(self):
        conn = self.imap
        conn.select()
        typ, data = conn.search(None, 'ALL')
        l = []
        try:
            for num in data[0].split():
                typ, msg_data = conn.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])
                        #print msg['Content-Type']
                        #payload=msg.get_payload()
                        #body=extract_body(payload)
                        #print(body)

                        # Convert header fields into dict
                        d = dict(msg) 
                        # Add other essential fields
                        d['body'] = self._extract_body(msg.get_payload())
                        d['_pyobj'] = utils.Serialize.dumps(msg)
                        l.append(utils.JsonDict(d))
                #typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
        finally:
            pass
            #try:
            #    conn.close()
            #except:
            #    pass
            ##conn.logout()
        return l

    def auth(self):
        imap_ok = False
        smtp_ok = False

        logger.debug("Try loggin IMAP server...")
        try:
            if self.imap:
                del self.imap
            self.imap = imaplib.IMAP4_SSL(self.jsonconf['imap_host'], self.jsonconf['imap_port'])
            self.imap.login(self.jsonconf['username'], self.jsonconf['password'])
            imap_ok = True
        except imaplib.IMAP4_SSL.error, e:
            if e.message.find("AUTHENTICATIONFAILED"):
                logger.warning("IMAP Authentication failed! Channel '%s'", self.jsonconf['channel_name'])
            else:
                raise e
        
        logger.debug("Try loggin SMTP server...")
        try:
            if self.smtp:
                del self.smtp
            self.smtp = smtplib.SMTP("%s:%s" % (self.jsonconf['smtp_host'], self.jsonconf['smtp_port']))  
            self.smtp.starttls()  
            self.smtp.login(self.jsonconf['username'], self.jsonconf['password'])
            smtp_ok = True
        except smtplib.SMTPAuthenticationError:
            logger.warning("SMTP Authentication failed! Channel '%s'", self.jsonconf['channel_name'])

        if imap_ok and smtp_ok:
            logger.info("Email channel '%s' auth success", self.jsonconf['channel_name'])
            return True
        else:
            logger.warning("Email channel '%s' auth failed!!", self.jsonconf['channel_name'])
            return False
            

    def _send(self, toaddr, title, msg):
        '''
        :param toaddr:
            The recipient, only one in a string. 

        :param msg:
            One email object, which supports as_string() method
        '''
        fromaddr = self.jsonconf['address']
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = title

        return self.smtp.sendmail(fromaddr, toaddr, msg.as_string())  

    def home_timeline(self, count = 20):
        r = self._receive()

        message_list = []
        for m in r:
            message_list.append(self.Message(
                    m,\
                    platform = self.jsonconf['platform'],\
                    channel = self.jsonconf['channel_name']\
                    ))

        return message_list


    def update(self, text):
        from email.mime.text import MIMEText
        msg = MIMEText(text, _charset = 'utf-8')
        return self._send('hpl1989@gmail.com', 'test from snsapi', msg)

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
