#-*- encoding: utf-8 -*-

'''
sqlite

We use sqlite3 as the backend.
'''

from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype
from ..utils import console_output
from .. import utils

import sqlite3

logger.debug("%s plugged!", __file__)

class SQLiteMessage(snstype.Message):
    platform = "SQLite"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.parsed = dct

class SQLite(SNSBase):

    Message = SQLiteMessage

    def __init__(self, channel = None):
        super(SQLite, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.con = None

    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'SQLite'
        c['url'] = ''
        return c

    def read_channel(self, channel):
        super(SQLite, self).read_channel(channel)

        if not 'username' in self.jsonconf:
            self.jsonconf['username'] = 'snsapi_sqlite_username'
        if not 'userid' in self.jsonconf:
            self.jsonconf['userid'] = 'snsapi_sqlite_userid'

    def _create_schema(self):
        cur = self.con.cursor()

        try:
            cur.execute("create table meta (time integer, path text)")
            cur.execute("insert into meta values (?,?)", (int(self.time()), self.jsonconf.url))
            self.con.commit()
        except sqlite3.OperationalError, e:
            if e.message == "table meta already exists":
                return
            else:
                raise e

        cur.execute("""
        CREATE TABLE message (
        id INTEGER PRIMARY KEY,
        time INTEGER,
        text TEXT,
        userid TEXT,
        username TEXT,
        mid TEXT,
        digest TEXT,
        digest_parsed TEXT,
        digest_full TEXT,
        parsed TEXT,
        full TEXT
        )
        """)
        self.con.commit()

    def _connect(self):
        '''
        Connect to SQLite3 database and create cursor.
        Also initialize the schema if necessary.

        '''
        url = self.jsonconf.url
        self.con = sqlite3.connect(url, check_same_thread = False)
        self.con.isolation_level = None
        self._create_schema()

    def auth(self):
        '''
        SQLite3 do not need auth.

        We define the "auth" procedure to be:

           * Close previously connected database.
           * Reconnect database using current config.

        '''
        logger.info("SQLite3 channel do not need auth. Try connecting to DB...")
        if self.con:
            self.con.close()
            self.con = None
        self._connect()

    def auth_first(self):
        logger.info("%s platform do not need auth_first!", self.platform)

    def auth_second(self):
        logger.info("%s platform do not need auth_second!", self.platform)

    def home_timeline(self, count = 20):
        message_list = snstype.MessageList()

        try:
            cur = self.con.cursor()
            r = cur.execute('''
            SELECT time,userid,username,text FROM message
            ORDER BY time DESC LIMIT ?
            ''', (count,))
            for m in r:
                message_list.append(self.Message({
                        'time':m[0],
                        'userid':m[1],
                        'username':m[2],
                        'text':m[3]
                        },\
                        platform = self.jsonconf['platform'],\
                        channel = self.jsonconf['channel_name']\
                        ))
        except Exception, e:
            logger.warning("Catch expection: %s", e)

        return message_list

    def _update_text(self, text):
        m = self.Message({\
                'time':int(self.time()),
                'userid':self.jsonconf['userid'],
                'username':self.jsonconf['username'],
                'text':text
                }, \
                platform = self.jsonconf['platform'],\
                channel = self.jsonconf['channel_name']\
                )
        return self._update_message(m)

    def _update_message(self, message):
        cur = self.con.cursor()

        try:
            cur.execute('''
            INSERT INTO message(time,userid,username,text,mid,digest,digest_parsed,digest_full,parsed,full)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ''', (\
                    message.parsed.time,\
                    message.parsed.userid,\
                    message.parsed.username,\
                    message.parsed.text,\
                    str(message.ID),\
                    message.digest(),\
                    message.digest_parsed(),\
                    message.digest_full(),\
                    message.dump_parsed(),
                    message.dump_full()
                    ))
            return True
        except Exception, e:
            logger.warning("failed: %s", str(e))
            return False

    def update(self, text):
        if isinstance(text, str):
            return self._update_text(text)
        elif isinstance(text, unicode):
            return self._update_text(text)
        elif isinstance(text, snstype.Message):
            return self._update_message(text)
        else:
            logger.warning('unknown type: %s', type(text))
            return False

    def expire_after(self, token = None):
        # This platform does not have token expire issue.
        return -1
