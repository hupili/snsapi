# -*- encoding: utf-8 -*-

'''
twitter

We use python-twitter as the back-end at present.
It should be changed to invoke REST API directly later.
'''
if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
    import utils
    from third import twitter
else:
    from ..snslog import SNSLog
    logger = SNSLog
    from ..snsbase import SNSBase
    from .. import snstype
    from ..utils import console_output
    from .. import utils
    from ..third import twitter

logger.debug("%s plugged!", __file__)


class TwitterStatusMessage(snstype.Message):

    platform = "TwitterStatus"

    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.id = dct['id']

        self.parsed.time = utils.str2utc(dct['created_at'])
        # NOTE:
        #   * dct['user']['screen_name'] is the path part of user's profile URL.
        #   It is actually in a position of an id. You should @ this string in
        #   order to mention someone.
        #   * dct['user']['name'] is actually a nick name you can set. It's not
        #   permanent.
        self.parsed.username = dct['user']['screen_name']
        self.parsed.userid = dct['user']['id']
        self.parsed.text = dct['text']


class TwitterStatus(SNSBase):

    Message = TwitterStatusMessage

    def __init__(self, channel=None):
        super(TwitterStatus, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.api = twitter.Api(consumer_key=self.jsonconf['app_key'],
                consumer_secret=self.jsonconf['app_secret'],
                access_token_key=self.jsonconf['access_key'],
                access_token_secret=self.jsonconf['access_secret'])

    @staticmethod
    def new_channel(full=False):
        c = SNSBase.new_channel(full)

        c['platform'] = 'TwitterStatus'
        c['app_key'] = ''
        c['app_secret'] = ''
        c['access_key'] = ''
        c['access_secret'] = ''

        return c

    def read_channel(self, channel):
        super(TwitterStatus, self).read_channel(channel)
        self.jsonconf['text_length_limit'] = 140

    def auth(self):
        logger.info("Current implementation of Twitter does not use auth!")

    def home_timeline(self, count=20):
        '''
        NOTE: this does not include your re-tweeted statuses.
        It's another interface to get re-tweeted status on Twitter.
        We'd better save a call.
        Deprecate the use of retweets.
        See reply and forward of this platform for more info.
        '''
        status_list = snstype.MessageList()
        try:
            statuses = self.api.GetHomeTimeline(count=count)
            for s in statuses:
                status_list.append(self.Message(s.AsDict(),
                        self.jsonconf['platform'],
                        self.jsonconf['channel_name']))
            logger.info("Read %d statuses from '%s'", len(status_list), self.jsonconf['channel_name'])
        except Exception, e:
            logger.warning("Catch exception: %s", e)
        return status_list

    def update(self, text):
        text = self._cat(self.jsonconf['text_length_limit'], [(text, 1)])
        try:
            status = self.api.PostUpdate(text)
            # TODO:
            #     Find better indicator for status update success
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Twitter failed: %s', str(e))
            return False

    def reply(self, statusID, text):
        text = self._cat(self.jsonconf['text_length_limit'], [(text, 1)])
        try:
            status = self.api.PostUpdate(text,
                                         in_reply_to_status_id=statusID.id)
            # TODO:
            #     Find better indicator for status update success
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Twitter failed: %s', str(e))
            return False

    def forward(self, message, text):
        if not message.platform == self.platform:
            return super(TwitterStatus, self).forward(message, text)
        else:
            decorated_text = self._cat(self.jsonconf['text_length_limit'],
                    [(text, 2),
                     ('@' + message.parsed.username + ' ' + message.parsed.text, 1)],
                    delim='//')
            try:
                status = self.api.PostUpdate(decorated_text)
                # TODO:
                #     Find better indicator for status update success
                if status:
                    return True
                else:
                    return False
            except Exception, e:
                logger.warning('update Twitter failed: %s', str(e))
                return False

    def like(self, message):
        '''
        Like method
           * Twitter doesn't provide an API for "like"
           * So "favourite" function supersedes "like"
           * Here "like" means "add to my favourites"
           * Receive a message
        '''
        try:
            status = self.api.CreateFavorite(id=message.ID.id)
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('like tweet failed: %s', e)
            return False

    def unlike(self, message):
        '''
        UnLike method
           * Twitter doesn't provide an API for "unlike"
           * So "unfavourite" function supersedes "unlike"
           * Here "unlike" means "delete from my favourites"
           * Receive a message
        '''
        try:
            status = self.api.DestroyFavorite(id=message.ID.id)
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('like tweet failed: %s', e)
            return False

    def expire_after(self, token=None):
        # This platform does not have token expire issue.
        return -1


class TwitterSearchMessage(TwitterStatusMessage):

    platform = "TwitterSearch"


class TwitterSearch(TwitterStatus):

    Message = TwitterSearchMessage

    @staticmethod
    def new_channel(full=False):
        c = TwitterStatus.new_channel(full)
        c['platform'] = 'TwitterSearch'
        c['term'] = 'snsapi'
        c['include_entities'] = True
        return c

    def __init__(self, channel=None):
        super(TwitterSearch, self).__init__(channel)
        self.platform = self.__class__.__name__

        self.api = twitter.Api(consumer_key=self.jsonconf['app_key'],
                consumer_secret=self.jsonconf['app_secret'],
                access_token_key=self.jsonconf['access_key'],
                access_token_secret=self.jsonconf['access_secret'])

    def home_timeline(self, count=100):
        status_list = snstype.MessageList()
        try:
            # statuses = self.api.GetHomeTimeline(count = count)
            statuses = self.api.GetSearch(term=self.jsonconf['term'],
                            include_entities=self.jsonconf['include_entities'],
                            count=count)
            for s in statuses:
                status_list.append(self.Message(s.AsDict(),
                        self.jsonconf['platform'],
                        self.jsonconf['channel_name']))
            logger.info("Read %d statuses from '%s'", len(status_list), self.jsonconf['channel_name'])
        except Exception, e:
            logger.warning("Catch exception: %s", e)
        return status_list


if __name__ == '__main__':

    print '\n\n\n'
    print '==== SNSAPI Demo of twitter.py module ====\n'
    # Create and fill in app information
    twitter_conf = TwitterStatus.new_channel()
    twitter_conf['channel_name'] = 'test_twitter'
    twitter_conf['app_secret'] = ""             # Add your own keys
    twitter_conf['app_key'] = ""                # Add your own keys
    twitter_conf['access_key'] = ''             # Add your own keys
    twitter_conf['access_secret'] = ''          # Add your own keys
 
    # Instantiate the channel
    twi = TwitterStatus(twitter_conf)
    # OAuth your app
    print 'SNSAPI is going to authorize your app.'
    print 'Please make sure:'
    print '   * You have filled in your own app_key and app_secret in this script.'
    print 'Press [Enter] to continue or Ctrl+C to end.'
    raw_input()
    twi.auth()
    # Test get 2 messages from your timeline
    status_list = twi.home_timeline(2)
    print '\n\n--- Statuses of your friends is followed ---'
    print status_list
    print '--- End of status timeline ---\n\n'
    
    print 'Short demo ends here! You can do more with SNSAPI!'
    print 'Please join our group for further discussions'
