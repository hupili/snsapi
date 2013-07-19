#-*- encoding: utf-8 -*-

'''
email platform

Support get message by IMAP and send message by SMTP

The file is named as "emails.py" instead of "email.py"
because there is a package in Python called "email".
We will import that package..

Premature warning:
   * This is platform is only tested on GMail so far.
   * Welcome to report test results of other platform.

'''

from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase, require_authed
from .. import snstype
from ..utils import console_output
from .. import utils
from ..utils import json

import time
import email
from email.mime.text import MIMEText
from email.header import decode_header, make_header
import imaplib
import smtplib

import base64
import re

logger.debug("%s plugged!", __file__)

class EmailMessage(snstype.Message):
    platform = "Email"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _decode_header(self, header_value):
        ret = unicode()
        #print decode_header(header_value)
        for (s,e) in decode_header(header_value):
            ret += s.decode(e) if e else s
        return ret

    def _parse(self, dct):
        #TODO:
        #    Put in message id.
        #    The id should be composed of mailbox and id in the box.
        #
        #    The IMAP id can not be used as a global identifier.
        #    Once messages are deleted or moved, it will change.
        #    The IMAP id is more like the subscript of an array.
        #
        #    SNSAPI should work out its own message format to store an
        #    identifier. An identifier should be (address, sequence).
        #    There are three ways to generate the sequence number:
        #       * 1. Random pick
        #       * 2. Pass message through a hash
        #       * 3. Maintain a counter in the mailbox
        #       * 4. UID as mentioned in some discussions. Not sure whether
        #       this is account-dependent or not.
        #
        #     I prefer 2. at present. Our Message objects are designed
        #     to be able to digest themselves.

        self.parsed.title = self._decode_header(dct.get('Subject'))
        self.parsed.text = dct.get('body')
        self.parsed.time = utils.str2utc(dct.get('Date'))

        sender = dct.get('From')
        r = re.compile(r'^(.+)<(.+@.+\..+)>$', re.IGNORECASE)
        m = r.match(sender)
        if m:
            self.parsed.username = m.groups()[0].strip()
            self.parsed.userid = m.groups()[1].strip()
        else:
            self.parsed.username = sender
            self.parsed.userid = sender

        #TODO:
        #    The following is just temporary method to enable reply email.
        #    See the above TODO for details. The following information
        #    suffices to reply email. However, they do not form a real ID.
        self.ID.title = self.parsed.title
        self.ID.reply_to = dct.get('Reply-To', self.parsed.userid)

class Email(SNSBase):

    Message = EmailMessage

    def __init__(self, channel = None):
        super(Email, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.imap = None
        self.imap_ok = False
        self.smtp = None
        self.smtp_ok = False

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

    def __decode_email_body(self, payload, msg):
        ret = payload
        if 'Content-Transfer-Encoding' in msg:
            transfer_enc = msg['Content-Transfer-Encoding'].strip()
            if transfer_enc == "base64":
                ret = base64.decodestring(ret)
            elif transfer_enc == "7bit":
                #TODO:
                #    It looks like 7bit is just ASCII standard.
                #    Do nothing.
                #    Check whether this logic is correct?
                pass
            else:
                logger.warning("unknown transfer encoding: %s", transfer_enc)
                return "(Decoding Failed)"
        # The past content-type fetching codes.
        # It's better to rely on email.Message functions.
        #
        #if 'Content-Type' in msg:
        #    ct = msg['Content-Type']
        #    r = re.compile(r'^(.+); charset="(.+)"$', re.IGNORECASE)
        #    m = r.match(ct)
        #    # Use search if the pattern does not start from 0.
        #    # Use group() to get matched part and groups() to get
        #    # mateched substrings.
        #    if m:
        #        cs = m.groups()[1]
        #    else:
        #        # By default, we assume ASCII charset
        #        cs = "ascii"
        #    try:
        #        ret = ret.decode(cs)
        #    except Exception, e:
        #        #logger.warning("Decoding payload '%s' using '%s' failed!", payload, cs)
        #        return "(Decoding Failed)"

        try:
            cs = msg.get_content_charset()
            ret = ret.decode(cs)
        except Exception, e:
            return "(Decoding Failed)"

        return ret

    def _extract_body(self, payload, msg):
        if isinstance(payload,str):
            return self.__decode_email_body(payload, msg)
        else:
            return '\n'.join([self._extract_body(part.get_payload(), msg) for part in payload])

    def _get_text_plain(self, msg):
        '''
        Extract text/plain section from a multipart message.

        '''
        tp = None
        if not msg.is_multipart():
            if msg.get_content_type() == 'text/plain':
                tp = msg
            else:
                return u"No text/plain found"
        else:
            for p in msg.walk():
                if p.get_content_type() == 'text/plain':
                    tp = p
                    break
        if tp:
            return self.__decode_email_body(tp.get_payload(), tp)
        else:
            return u"No text/plain found"

    def _format_from_text_plain(self, text):
        '''
        Some text/plain message is sent from email services.
        The formatting is not SNSAPI flavoured. To work around
        this and enable unified view, we use this function
        to do post-formatting.

        '''
        return text.replace('>', '').replace('\r\n', '').replace('\n', '')

    def _wait_for_email_subject(self, sub):
        conn = self.imap
        conn.select('INBOX')
        num = None
        while (num is None):
            logger.debug("num is None")
            typ, data = conn.search(None, '(Subject "%s")' % sub)
            num = data[0].split()[0]
            time.sleep(0.5)
        return num

    def _get_buddy_list(self):
        # 1. Get buddy_list from "buddy" folder

        (typ, data) = self.imap.create('buddy')
        conn = self.imap
        conn.select('buddy')

        self.buddy_list = {}
        num = None
        self._buddy_message_id = None
        try:
            typ, data = conn.search(None, 'ALL')
            # We support multiple emails in "buddy" folder.
            # Each of the files contain a json list. We'll
            # merge all the list and use it as the buddy_list.
            for num in data[0].split():
                typ, msg_data = conn.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])
                        text = self._extract_body(msg.get_payload(), msg)
                        logger.debug("Extract part text: %s", text.rstrip())
                        try:
                            self.buddy_list.update(json.loads(text))
                        except Exception, e:
                            logger.warning("Extend list with '%s' failed!", e)
            logger.debug("reading buddylist successful: %s", self.buddy_list)
        except Exception, e:
            logger.warning("catch exception when trying to read buddylist %s", e)
            pass

        if self.buddy_list is None:
            logger.debug("buddy list is None")
            self.buddy_list = {}

        # 2. Get buddy_list from local conf files

        if "manual_buddy_list" in self.jsonconf:
            for b in self.jsonconf['manual_buddy_list']:
                self.buddy_list[b['userid']] = b

    def _update_buddy_list(self):
        conn = self.imap

        # The unique identifier for a buddy_list
        title = 'buddy_list:' + str(self.time())
        from email.mime.text import MIMEText
        msg = MIMEText(json.dumps(self.buddy_list))
        self._send(self.jsonconf['address'], title, msg)

        # Wait for the new buddy_list email to arrive
        mlist = self._wait_for_email_subject(title)
        logger.debug("returned message id: %s", mlist)

        # Clear obsolete emails in "buddy" box
        conn.select('buddy')
        typ, data = conn.search(None, 'ALL')
        for num in data[0].split():
            conn.store(num, '+FLAGS', r'(\deleted)')
            logger.debug("deleting message '%s' from 'buddy'", num)

        # Move the new buddy_list email from INBOX to "buddy" box
        conn.select('INBOX')
        conn.copy(mlist, 'buddy')
        conn.store(mlist, '+FLAGS', r'(\deleted)')

    def add_buddy(self, address, nickname = None):
        '''
        Warning: Use this function only when necessary. (20121026)

        We have not abstracted User class yet. The first step for SNSAPI
        is to abstract the information flow. That is the Message class
        you see. We assume buddy_list is maintained in other offline manner.
        e.g. Users login Sina Weibo and change their buddy list. In the
        next milestone, we may consider abstract User class. In the current
        framework, we need some esential function to manage buddy_list on
        email platform. This is why the currrent function is here. The
        interface may be (drastically) changed in the future.

        The better way for upper layer developers is to operate
        'self.buddy_list' directly following the format.

        '''
        #self.buddy_list.append({"userid": address, "username": nickname})
        self.buddy_list[address] = {"userid": address, "username": nickname}
        self._update_buddy_list()

    def _receive(self, count = 20):
        #TODO:
        #    1.
        #    Consider UNSEEN message first. If we get less than count
        #    number of messages, then search for 'ALL'.
        #
        #    2.
        #    Make a separate box for snsapi. According to configs,
        #    search for all messages or snsapi formated messages.
        #    For snsapi formated messages, move them to this mailbox.

        # Check out all the email IDs
        conn = self.imap
        conn.select('INBOX')
        typ, data = conn.search(None, 'ALL')
        #logger.debug("read message IDs: %s", data)

        # We assume ID is in chronological order and filter
        # the count number of latest messages.
        latest_messages = sorted(data[0].split(), key = lambda x: int(x), reverse = True)[0:count]
        #logger.debug("selected message IDs: %s", latest_messages)

        message_list = []
        try:
            #for num in data[0].split():
            for num in latest_messages:
                typ, msg_data = conn.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])

                        #TODO:
                        #    Parse header fields. Header fields can also be
                        #    encoded, e.g. UTF-8.
                        #
                        #    email.header.decode_header() may help.
                        #
                        #    There are some ill-formated senders, e.g. Baidu Passport.
                        #    See the link for workaround:
                        #    http://stackoverflow.com/questions/7331351/python-email-header-decoding-utf-8

                        # Convert header fields into dict
                        d = dict(msg)
                        d['body'] = self._format_from_text_plain(self._get_text_plain(msg))
                        d['_pyobj'] = utils.Serialize.dumps(msg)
                        message_list.append(utils.JsonDict(d))
        except Exception, e:
            logger.warning("Error when making message_list: %s", e)
        return message_list

    def auth(self):
        #TODO:
        #    login here once is not enough.
        #    If the client stays idle for a long time,
        #    it will disconnect from the server. So in
        #    later transactions, we should check and
        #    login again if necessary.
        #
        #    The error caught is "socket error: EOF"

        imap_ok = False
        smtp_ok = False

        logger.debug("Try login IMAP server...")
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

        logger.debug("Try login SMTP server...")
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
            self.imap_ok = True
            self.smtp_ok = True
            logger.info("Email channel '%s' auth success", self.jsonconf['channel_name'])
            self._get_buddy_list()
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
        msg['Subject'] = make_header([(self._unicode_encode(title), 'utf-8')])

        try:
            self.smtp.sendmail(fromaddr, toaddr, msg.as_string())
            return True
        except Exception, e:
            if e.message.count("socket error: EOF"):
                logger.debug("Catch EOF. Reconnect...")
                self.auth()
            logger.warning("Catch exception: %s", e)
            return False

    @require_authed
    def home_timeline(self, count = 20):
        try:
            r = self._receive(count)
        except Exception, e:
            if e.message.count("socket error: EOF"):
                logger.debug("Catch EOF. Reconnect...")
                self.auth()
            logger.warning("Catch exception: %s", e)
            return snstype.MessageList()

        message_list = snstype.MessageList()
        try:
            for m in r:
                message_list.append(self.Message(
                        m,\
                        platform = self.jsonconf['platform'],\
                        channel = self.jsonconf['channel_name']\
                        ))
        except Exception, e:
            logger.warning("Catch expection: %s", e)

        logger.info("Read %d statuses from '%s'", len(message_list), self.jsonconf.channel_name)
        return message_list

    def _send_to_all_buddy(self, title, msg):
        ok_all = True
        for u in self.buddy_list.values():
            toaddr = u['userid'] #userid of email platform is email address
            re = self._send(toaddr, title, msg)
            logger.debug("Send email to '%s': %s", toaddr, re)
            ok_all = ok_all and re
        return ok_all

    @require_authed
    def update(self, text, title = None):
        '''
        :title:
            The unique field of email. Other platforms do not use it. If not supplied,
            we'll format a title according to SNSAPI convention.
        '''
        msg = MIMEText(text, _charset = 'utf-8')
        if not title:
            #title = '[snsapi][status][from:%s][timestamp:%s]' % (self.jsonconf['address'], str(self.time()))
            title = '[snsapi][status]%s' % (text[0:10])
        return self._send_to_all_buddy(title, msg)

    @require_authed
    def reply(self, statusID, text):
        """reply status
        @param status: StatusID object
        @param text: string, the reply message
        @return: success or not
        """
        msg = MIMEText(text, _charset = 'utf-8')
        title = "Re:" + statusID.title
        toaddr = statusID.reply_to
        return self._send(toaddr, title, msg)

    def expire_after(self, token = None):
        # Check whether the user supplied secrets are correct
        if self.imap_ok == True and self.smtp_ok == True:
            # -1: Means this platform does not have token expire issue.
            #     More precisely, when the secrets are correct,
            #     you can re-login at any time. Same effect as
            #     refresing the token of OSN.
            return -1
        else:
            # 0: Means it has already expired. The effect of incorrect
            #    secrets is same as expired.
            return 0

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
