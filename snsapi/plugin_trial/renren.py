# -*- encoding: utf-8 -*-

'''
Renren Client

'''

if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
    from snstype import BooleanWrappedData
    import utils
    import time
    import urllib
    import json
else:
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from ..snstype import BooleanWrappedData
    from .. import snstype
    from .. import utils
    import time
    import urllib

logger.debug("%s plugged!", __file__)

# Inteface URLs.
# This differs from other platforms
RENREN_AUTHORIZATION_URI = "http://graph.renren.com/oauth/authorize"
RENREN_ACCESS_TOKEN_URI = "http://graph.renren.com/oauth/token"
RENREN_API_SERVER = "https://api.renren.com/restserver.do"
RENREN_API2_SERVER = "https://api.renren.com/v2/"

# This error is moved back to "renren.py".
# It's platform specific and we do not expect other
# file to raise this error.


class RenrenAPIError(Exception):

    def __init__(self, code, message):
        super(RenrenAPIError, self).__init__(message)
        self.code = code


class RenrenFeedMessage(snstype.Message):

    platform = "RenrenFeed"

    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.status_id = dct['id']
        self.ID.source_user_id = self.parsed.userid = str(dct['sourceUser']['id'])
        self.parsed.username = dct['sourceUser']['name']
        self.parsed.time = utils.str2utc(dct['time'], " +08:00")
        self.parsed.text = ""
        self.ID.feed_type = self.parsed.feed_type = dct['type']
        try:
            if self.ID.feed_type == "PUBLISH_ONE_PHOTO" or self.ID.feed_type == "PUBLISH_MORE_PHOTO":
                self.ID.resource_id = dct["attachment"][0]["id"]
            else:
                self.ID.resource_id = dct["resource"]["id"]
        except Exception, e:
            logger.warning(str(e))
            self.ID.resource_id = self.ID.status_id
        ORIG_USER = 'orig'

        if 'attachment' in dct and dct['attachment']:
            for at in dct['attachment']:
                if 'ownerId' in at and at['ownerId']:
                    ORIG_USER = at['ownerId']
                    self.parsed.username_orig = ORIG_USER
        if 'message' in dct:
            self.parsed.text += dct['message']
        if str(dct['type']) == "SHARE":
            self.parsed.text += u" //" + ORIG_USER + ":"
        if 'title' in dct['resource'] and dct['resource']['title']:
            if 'message' not in dct or dct['message'] != dct['resource']['title']:
                self.parsed.text += ' "' + dct['resource']['title'] + '" '

        if 'content' in dct['resource'] and dct['resource']['content']:
            self.parsed.text += dct['resource']['content'] + "//"
        if 'url' in dct['resource'] and dct['resource']['url']:
            self.parsed.text += dct['resource']['url'][0:-10]
        if 'attachment' in dct and dct['attachment']:
            for at in dct['attachment']:
                if str(at['type']) == 'PHOTO':
                    if ('rawImageUrl' in at and at['rawImageUrl']):
                        data = at['rawImageUrl']
                    else:
                        data = at['orginalUrl']

                    self.parsed.attachments.append(
                        {
                            'type': 'picture',
                            'format': ['link'],
                            # FIXME: page photo don't have raw_src
                            'data': data
                        }
                    )
                elif 'url' in at:
                    attype = 'link'
                    if str(at['type']) in ['ALBUM', 'BLOG']:
                        attype = str(at['type'])
                    self.parsed.attachments.append(
                        {
                            'type': attype,
                            'format': ['link'],
                            'data': at['url']
                        })


class RenrenStatusMessage(RenrenFeedMessage):

    platform = 'RenrenStatus'


class RenrenShareMessage(RenrenFeedMessage):

    platform = 'RenRenShare'


class RenrenBlogMessage(RenrenFeedMessage):

    platform = 'RenrenBlog'


class RenrenPhotoMessage(RenrenFeedMessage):

    platform = 'RenrenPhoto'


class RenrenFeed(SNSBase):

    Message = RenrenFeedMessage

    def __init__(self, channel=None):
        super(RenrenFeed, self).__init__(channel)
        self.platform = self.__class__.__name__

    @staticmethod
    def new_channel(full=False):
        c = SNSBase.new_channel(full)

        c['app_key'] = ''
        c['app_secret'] = ''
        c['platform'] = 'RenrenFeed'
        c['auth_info'] = {
                "save_token_file": "(default)",
                "cmd_request_url": "(default)",
                "callback_url": "http://snsapi.ie.cuhk.edu.hk/aux/auth.php",
                "cmd_fetch_code": "(default)"
                }
        return c

    def renren_request(self, method=None, **kwargs):
        return self._renren_request_v2(method, **kwargs)

    def _renren_request_v2_bearer_token(self, method=None, **kwargs):
        kwargs['access_token'] = self.token.access_token
        if '_files' in kwargs:
            _files = kwargs['_files']
            del kwargs['_files']
        else:
            _files = {}
        if _files:
            args = urllib.urlencode(kwargs)
            response = self._http_post(RENREN_API2_SERVER + method + '?' + args, {}, files=_files)
        else:
            response = self._http_get(RENREN_API2_SERVER + method, kwargs)
        # logger.debug('response: %s', response)
        if response == {} or 'error' in response:
            if 'error' in response:
                logger.warning(response['error']['message'])
            else:
                logger.warning("error")
        return response

    def _renren_request_v2(self, method=None, **kwargs):
        '''
        A general purpose encapsulation of renren API.
        It fills in system paramters and compute the signature.
        Return a list on success
        raise Exception on error
        '''
        kwargs['access_token'] = self.token.access_token
        kwargs['format'] = 'json'
        if 'file' in kwargs:
            _files = kwargs['file']
            del kwargs['file']
        else:
            _files = {}

        if method == "feed/list" or method == "status/list":
            response = self._http_get(RENREN_API2_SERVER + method, kwargs)
        else:
            response = self._http_post(RENREN_API2_SERVER + method, kwargs, files=_files)

        if type(response) is not list and "error" in response:
            raise RenrenAPIError(response["error"]["code"], response["error"]["message"])
        return response['response']

    def _renren_request_v1_no_sig(self, method=None, **kwargs):
        '''
        A general purpose encapsulation of renren API.
        It fills in system paramters and compute the signature.
        Return a list on success
        raise Exception on error
        '''

        kwargs['method'] = method
        kwargs['access_token'] = self.token.access_token
        kwargs['v'] = '1.0'
        kwargs['format'] = 'json'
        if '_files' in kwargs:
            _files = kwargs['_files']
            del kwargs['_files']
        else:
            _files = {}
        response = self._http_post(RENREN_API_SERVER, kwargs, files=_files)

        if type(response) is not list and "error_code" in response:
            logger.warning(response["error_msg"])
            raise RenrenAPIError(response["error_code"], response["error_msg"])
        return response

    def auth_first(self):
        '''
        docstring placeholder
        '''

        args = {"client_id": self.jsonconf.app_key,
                "redirect_uri": self.auth_info.callback_url}
        args["response_type"] = "code"
        args["scope"] = " ".join(["read_user_feed",
                                  "read_user_status",
                                  "read_user_blog",
                                  "status_update",
                                  "publish_comment",
                                  "publish_blog",
                                  "publish_share",
                                  "publish_feed",
                                  "status_update",
                                  "photo_upload",
                                  "operate_like"])

        url = RENREN_AUTHORIZATION_URI + "?" + self._urlencode(args)
        self.request_url(url)

    def auth_second(self):
        '''
        docstring placeholder
        '''

        try:
            url = self.fetch_code()
            self.token = self._parse_code(url)
            args = dict(client_id=self.jsonconf.app_key, redirect_uri=self.auth_info.callback_url)
            args["client_secret"] = self.jsonconf.app_secret
            args["code"] = self.token.code
            args["grant_type"] = "authorization_code"
            self.token.update(self._http_get(RENREN_ACCESS_TOKEN_URI, args))
            if hasattr(self.token, "expires_in"):
                self.token.expires_in = self.token.expires_in + self.time()
            else:
                self.token.expires_in = self.time() + 60 * 60 * 7 * 24
            # In case that no "expires_in" property is returned.
        except Exception, e:
            logger.warning("Auth second fail. Catch exception: %s", str(e))
            self.token = None

    def auth(self):
        '''
        docstring placeholder
        '''

        if self.get_saved_token():
            return

        logger.info("Try to authenticate '%s' using OAuth2", self.jsonconf.channel_name)
        self.auth_first()
        self.auth_second()
        if not self.token:
            return False
        self.save_token()
        logger.debug("Authorized! access token is " + str(self.token))
        logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)

    def need_auth(self):
        return True

    @require_authed
    def home_timeline(self, count=20, **kwargs):
        # FIXME: automatic paging for count > 100
        # BUG: It seems that ttype has no influence
        # on the returned value of renren_request()
        ttype = 'ALL'
        if 'type' in kwargs:
            ttype = kwargs['type']

        try:
            jsonlist = self.renren_request(
                method="feed/list",
                page=1,
                count=count,
                type=ttype,
            )
        except RenrenAPIError, e:
            logger.warning("RenrenAPIError, %s", e)
            return snstype.MessageList()
        statuslist = snstype.MessageList()
        for j in jsonlist:
            try:
                statuslist.append(self.Message(
                    j,
                    platform=self.jsonconf['platform'],
                    channel=self.jsonconf['channel_name']
                ))
            except Exception, e:
                logger.warning("Catch exception: %s", e)

        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf['channel_name'])
        return statuslist

    def _update_status(self, text):
        try:
            self.renren_request(
                method='status/put',
                content=text
            )
            return BooleanWrappedData(True)
        except:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })

    def _update_blog(self, text, title):
        try:
            self.renren_request(
                method='blog/put',
                title=title,
                content=text
            )
            return BooleanWrappedData(True)
        except:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })

    def _update_share_link(self, text, link):
        try:
            self.renren_request(
                method='share/url/put',
                url=link,
                comment=text
            )
            return BooleanWrappedData(True)
        except:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_']
            })

    def _update_photo(self, text, pic):
        try:
            self.renren_request(
                method='photo/upload',
                description=text,
                file={'upload': ('%d.jpg' % int(time.time()), pic)}
            )
            return BooleanWrappedData(True)
        except:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })

    def _dummy_update(self, text, **kwargs):
        return False

    @require_authed
    def update(self, text, **kwargs):
        coder = int(''.join(map(lambda t: str(int(t)),
                               [
                                   'title' in kwargs,
                                   'link' in kwargs,
                                   'pic' in kwargs
                               ][::-1])
                    ))
        try:
            update_what = {
                0: self._update_status,
                1: self._update_blog,
                10: self._update_share_link,
                100: self._update_photo
            }[coder]
        except:
            return BooleanWrappedData(False, {
                'errors': ['SNSAPI_NOT_SUPPORTED'],
            })
        return update_what(text, **kwargs)

    @require_authed
    def reply(self, statusId, text):
        res = None
        flag = False
        try:
            # The order in the bracket is important since there
            # exists "SHARE_XXXX" type. In order to figure out
            # the actual type, SHARE must be put in the first position.
            for msg_type in ["SHARE", "BLOG", "PHOTO", "ALBUM", "STATUS", "VIDEO"]:
                if msg_type in statusId.feed_type:
                    flag = True
                    break
            if flag:
                res = self.renren_request(
                    method="comment/put",
                    content=text,
                    commentType=msg_type,
                    entryOwnerId=statusId.source_user_id,
                    entryId=statusId.resource_id
                )
            else:
                return BooleanWrappedData(False, {
                    'errors': ['SNSAPI_NOT_SUPPORTED'],
                })
        except Exception, e:
            logger.warning('Catch exception: %s', e)
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })
        if res:
            return BooleanWrappedData(True)
        else:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })

    @require_authed
    def forward(self, message, text):
        res = None
        if not message.platform == self.platform:
            return super(RenrenFeed, self).forward(message, text)
        else:
            try:
                if message.ID.feed_type == 'UPDATE_STATUS':
                    res = self.renren_request(
                        method='status/share',
                        content=text,
                        statusId=message.ID.resource_id,
                        ownerId=message.ID.source_user_id,
                    )

                elif message.ID.feed_type != 'OTHER':
                    for msg_type in ["SHARE", "BLOG", "PHOTO", "ALBUM", "VIDEO"]:
                        if msg_type in message.ID.feed_type:
                            break
                    # The order in the bracket is important since there
                    # exists "SHARE_XXXX" type. In order to figure out
                    # the actual type, SHARE must be put in the first position.
                    res = self.renren_request(
                        method='share/ugc/put',
                        ugcType="TYPE_" + msg_type,
                        ugcId=message.ID.resource_id,
                        # Here message.ID.resource_id is the proper id
                        # for forwarding these messages instead of message.ID.status_id
                        ugcOwnerId=message.ID.source_user_id,
                        comment=text
                    )
                else:
                    return BooleanWrappedData(False, {
                        'errors': ['SNSAPI_NOT_SUPPORTED'],
                    })
            except Exception as e:
                logger.warning('Catch exception: %s', type(e))
                return BooleanWrappedData(False, {
                    'errors': ['PLATFORM_'],
                })
        if res:
            return BooleanWrappedData(True)
        else:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })
    
    @require_authed
    def like(self, message):
        res = None
        flag = False
        try:
            # The order in the bracket is important since there
            # exists "SHARE_XXXX" type. In order to figure out
            # the actual type, SHARE must be put in the first position.
            for msg_type in ["SHARE", "BLOG", "PHOTO", "ALBUM", "STATUS", "VIDEO"]:
                if msg_type in message.ID.feed_type:
                    flag = True
                    break
            if flag:
                res = self.renren_request(
                    method="like/ugc/put",
                    ugcOwnerId=message.ID.source_user_id,
                    likeUGCType="TYPE_" + msg_type,
                    ugcId=message.ID.resource_id
                )
            else:
                return BooleanWrappedData(False, {
                    'errors': ['SNSAPI_NOT_SUPPORTED'],
                })
        except Exception as e:
            logger.warning('Catch exception: %s', type(e))
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })
        if res:
            return BooleanWrappedData(True)
        else:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })

    @require_authed
    def unlike(self, message):
        res = None
        flag = False
        try:
            # The order in the bracket is important since there
            # exists "SHARE_XXXX" type. In order to figure out
            # the actual type, SHARE must be put in the first position.
            for msg_type in ["SHARE", "BLOG", "PHOTO", "ALBUM", "STATUS", "VIDEO"]:
                if msg_type in message.ID.feed_type:
                    flag = True
                    break
            if flag:
                res = self.renren_request(
                    method="like/ugc/remove",
                    ugcOwnerId=message.ID.source_user_id,
                    likeUGCType="TYPE_" + msg_type,
                    ugcId=message.ID.resource_id
                )
            else:
                return BooleanWrappedData(False, {
                    'errors': ['SNSAPI_NOT_SUPPORTED'],
                })
        except Exception as e:
            logger.warning('Catch exception: %s', type(e))
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })
        if res:
            return BooleanWrappedData(True)
        else:
            return BooleanWrappedData(False, {
                'errors': ['PLATFORM_'],
            })


class RenrenStatus(RenrenFeed):

    Message = RenrenStatusMessage

    def __init__(self, channel=None):
        super(RenrenStatus, self).__init__(channel)

    @staticmethod
    def new_channel(full=False):
        c = RenrenFeed.new_channel(full)
        c['platform'] = 'RenrenStatus'
        return c

    @require_authed
    def home_timeline(self, count=20):
        return RenrenFeed.home_timeline(self, count, type='UPDATE_STATUS')

    @require_authed
    def update(self, text):
        return RenrenFeed._update_status(self, text)


class RenrenBlog(RenrenFeed):

    Message = RenrenBlogMessage

    def __init__(self, channel=None):
        super(RenrenBlog, self).__init__(channel)

    @staticmethod
    def new_channel(full=False):
        c = RenrenFeed.new_channel(full)
        c['platform'] = 'RenrenBlog'
        return c

    @require_authed
    def home_timeline(self, count=20):
        return RenrenFeed.home_timeline(self, count, type='PUBLISH_BLOG,SHARE_BLOG')

    @require_authed
    def update(self, text, title=None):
        if not title:
            title = text.split('\n')[0]
        return RenrenFeed._update_blog(self, text, title)


class RenrenPhoto(RenrenFeed):

    Message = RenrenPhotoMessage

    def __init__(self, channel=None):
        super(RenrenPhoto, self).__init__(channel)

    @staticmethod
    def new_channel(full=False):
        c = RenrenFeed.new_channel(full)
        c['platform'] = 'RenrenPhoto'
        return c

    @require_authed
    def home_timeline(self, count=20):
        return RenrenFeed.home_timeline(self, count, type='PUBLISH_ONE_PHOTO,PUBLISH_MORE_PHOTO')

    @require_authed
    def update(self, text, pic=None):
        return self._update_photo(text, pic)


class RenrenShare(RenrenFeed):

    Message = RenrenShareMessage

    def __init__(self, channel=None):
        super(RenrenShare, self).__init__(channel)

    @staticmethod
    def new_channel(full=False):
        c = RenrenFeed.new_channel(full)
        c['platform'] = 'RenrenShare'
        return c

    @require_authed
    def home_timeline(self, count=20):
        return RenrenFeed.home_timeline(self, count, type='SHARE_BLOG,SHARE_LINK,SHARE_PHOTO,SHARE_ALBUM,SHARE_VIDEO')

    @require_authed
    def update(self, text, link=None):
        if not link:
            link = text
            return RenrenFeed._update_share_link(self, text, link)


class RenrenStatusDirectMessage(snstype.Message):

    platform = "RenrenStatusDirect"

    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.status_id = dct['id']
        self.ID.source_user_id = dct['ownerId']
        self.ID.feed_type = 'STATUS'

        self.parsed.userid = str(dct['ownerId'])
        self.parsed.username = dct['name']
        self.parsed.time = utils.str2utc(dct['createTime'], " +08:00")
        self.parsed.text = dct['content']


class RenrenStatusDirect(RenrenFeed):

    Message = RenrenStatusDirectMessage

    def __init__(self, channel=None):
        super(RenrenStatusDirect, self).__init__(channel)

    @staticmethod
    def new_channel(full=False):
        c = RenrenFeed.new_channel(full)
        c['platform'] = 'RenrenStatusDirect'
        c['friend_list'] = [
                    {
                    "username": "Name",
                    "userid": "ID"
                    }
                ]
        return c

    @require_authed
    def update(self, text):
        return RenrenFeed._update_status(self, text)

    def _get_user_status_list(self, count, userid, username):
        try:
            jsonlist = self.renren_request(
                method="status/list",
                pageNumberint=1,
                pageSize=count,
                ownerId=userid,
            )
        except RenrenAPIError, e:
            logger.warning("RenrenAPIError, %s", e)
            return snstype.MessageList()

        statuslist = snstype.MessageList()
        for j in jsonlist:
            try:
                j['name'] = username
                statuslist.append(self.Message(
                    j,
                    platform=self.jsonconf['platform'],
                    channel=self.jsonconf['channel_name']
                ))
            except Exception, e:
                logger.warning("Catch exception: %s", e)
        return statuslist

    @require_authed
    def home_timeline(self, count=20):
        '''
        Return count ``Message`` for each uid configured.

        Configure 'friend_list' in your ``channel.json`` first.
        Or, it returns your own status list by default.
        '''
        statuslist = snstype.MessageList()
        for user in self.jsonconf['friend_list']:
            userid = user['userid']
            username = user['username']
            statuslist.extend(self._get_user_status_list(count, userid, username))
        logger.info("Read %d statuses from '%s'", len(statuslist), self.jsonconf['channel_name'])
        return statuslist
