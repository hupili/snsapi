#-*- encoding: utf-8 -*-

'''
Sina Weibo client
'''

if __name__ == '__main__':
    import sys
    import urllib2
    import urllib
    import re
    import lxml.html
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
    from utils import console_output
    import utils
else:
    import sys
    import urllib2
    import urllib
    import re
    import lxml.html
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from .. import snstype
    from ..utils import console_output
    from .. import utils


logger.debug("%s plugged!", __file__)


class SinaWeiboWapStatusMessage(snstype.Message):
    platform = 'SinaWeiboWapStatus'
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.parsed.time = dct['time']
        self.parsed.username = dct['author']
        self.parsed.text = dct['text']
        self.parsed.comments_count = dct['comments_count']
        self.parsed.reposts_count = dct['reposts_count']
        self.parsed.userid = dct['uid']
        if 'orig' in dct:
            self.parsed.has_orig = True
            self.parsed.orig_text = dct['orig']['text']
            self.parsed.orig_comments_count = dct['orig']['comments_count']
            self.parsed.orig_reposts_count = dct['orig']['reposts_count']
        else:
            self.parsed.has_orig = False
        self.ID.id = dct['id']


class SinaWeiboWapStatus(SNSBase):
    Message = SinaWeiboWapStatusMessage

    def __init__(self, channel = None):
        super(SinaWeiboWapStatus, self).__init__(channel)
        assert channel['auth_by'] in ['userpass', 'gsid']
        self.platform = self.__class__.__name__
        self.Message.platform = self.platform


    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)
        c['platform'] = 'SinaWeiboWapStatus'
        c['auth_by'] = 'userpass'
        c['username'] = 'root'
        c['password'] = 'password'
        return c

    def _process_req(self, req):
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19')
        return req


    def _get_weibo_homepage(self):
        req = urllib2.Request('http://weibo.cn/?gsid=' + self.token['gsid'])
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        return m

    def auth(self):
        if self.jsonconf['auth_by'] == 'gsid':
            self.token['gsid'] = self.jsonconf['gsid']
        elif self.jsonconf['auth_by'] == 'userpass':
            req = urllib2.Request('http://weibo.cn/dpool/ttt/login.php')
            req = self._process_req(req)
            data = {'uname' : self.jsonconf['username'], 'pwd': self.jsonconf['password'],
                    'l' : '', 'scookie' : 'on', 'submit' : '登录'}
            data = urllib.urlencode(data)
            response = urllib2.urlopen(req, data, timeout = 10)
            p = response.read()
            final_url = response.geturl()
            self.token = {'gsid' :  final_url[final_url.find('=') + 1:]}
        else:
            return False
        return self.is_authed()

    def is_authed(self):
        return '<input type="submit" value="发布" />' in self._get_weibo_homepage()


    @require_authed
    def _get_uid_by_pageurl(self, url):
        if re.search('\/u\/[0-9]*', url):
            return re.search('\/u\/([0-9]*)', url).group(1)
        req = urllib2.Request('http://weibo.cn' + url)
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        return re.search(r'\/([0-9]*)\/info', m).group(1)

    @require_authed
    def _get_weibo(self, page = 1):
        #FIXME: 获取转发和评论数应该修改为分析DOM而不是正则表达式（以免与内容重复）
        #FIXME: 对于转发的微博，原微博信息不足
        req = urllib2.Request('http://weibo.cn/?gsid=' + self.token['gsid'] + '&page=%d' % (page))
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        h = lxml.html.fromstring(m)
        weibos = []
        for i in h.find_class('c'):
            if i.get('id') and i.get('id')[0:2] == 'M_':
                weibo = None
                if i.find_class('cmt'): # 转发微博
                    weibo = {
                            'uid' : self._get_uid_by_pageurl(i.find_class('nk')[0].attrib['href']),
                            'author' : i.find_class('nk')[0].text,
                            'id': i.get('id')[2:],
                            'time': i.find_class('ct')[0].text.encode('utf-8').split(' ')[1].decode('utf-8'),
                            'text' : None,
                            'orig' : {
                                'text': i.find_class('ctt')[0].text_content(),
                                'comments_count' : 0,
                                'reposts_count' : 0
                                },
                            'comments_count' : 0,
                            'reposts_count' : 0
                            }
                    parent = i.find_class('cmt')[-1].getparent()
                    retweet_reason = re.sub(r'转发理由:(.*)赞\[[0-9]*\] 转发\[[0-9]*\] 评论\[[0-9]*\] 收藏.*$', r'\1', parent.text_content().encode('utf-8'))
                    weibo['text'] = retweet_reason.decode('utf-8')
                    zf = re.search(r'赞\[([0-9]*)\] 转发\[([0-9]*)\] 评论\[([0-9]*)\]', parent.text_content().encode('utf-8'))
                    if zf:
                        weibo['comments_count'] = int(zf.group(2))
                        weibo['reposts_count'] = int(zf.group(3))
                    zf = re.search(r'赞\[([0-9]*)\] 原文转发\[([0-9]*)\] 原文评论\[([0-9]*)\]', i.text_content().encode('utf-8'))
                    if zf:
                        weibo['orig']['comments_count'] = int(zf.group(2))
                        weibo['orig']['reposts_count'] = int(zf.group(3))
                else:
                    weibo = {'author' : i.find_class('nk')[0].text, 
                            'uid' : self._get_uid_by_pageurl(i.find_class('nk')[0].attrib['href']),
                            'text': i.find_class('ctt')[0].text_content(),
                            'id': i.get('id')[2:],
                            'time': i.find_class('ct')[0].text.encode('utf-8').split(' ')[1]
                            }
                    zf = re.search(r'赞\[([0-9]*)\] 转发\[([0-9]*)\] 评论\[([0-9]*)\]', i.text_content().encode('utf-8'))
                    if zf:
                        weibo['comments_count'] = int(zf.group(2))
                        weibo['reposts_count'] = int(zf.group(3))
                weibos.append(weibo)
        statuslist = snstype.MessageList()
        for i in weibos:
            statuslist.append(self.Message(i, platform = self.jsonconf['platform'],
                channel = self.jsonconf['channel_name']))
        return statuslist


    @require_authed
    def home_timeline(self, number):
        all_weibo = []
        page = 1
        while len(all_weibo) < number:
            weibos = self._get_weibo(page)
            all_weibo += weibos[0:min(len(weibos), number - len(all_weibo))]
            page += 1
        return all_weibo

    @require_authed
    def update(self, text):
        homepage = self._get_weibo_homepage()
        m = re.search('<form action="(/mblog/sendmblog?[^"]*)" accept-charset="UTF-8" method="post">', homepage).group(1)
        data = {'rl' : '0', 'content' : self._unicode_encode(text)}
        data = urllib.urlencode(data)
        req = urllib2.Request('http://weibo.cn' + m.replace('&amp;', '&'))
        req = self._process_req(req)
        opener = urllib2.build_opener()
        response = opener.open(req, data, timeout = 10)
        t = response.read()
        if '<div class="ps">发布成功' in t:
            return True
        else:
            return False

    @require_authed
    def reply(self, statusID, text):
        id = statusID.id
        url = 'http://weibo.cn/comment/%s?gsid=%s' % (id, self.token['gsid'])
        req = self._process_req(urllib2.Request(url))
        res = urllib2.build_opener().open(req, timeout = 10).read()
        addcomment_url = 'http://weibo.cn' +  \
                re.search('<form action="(/comments/addcomment?[^"]*)" method="post">', res).group(1).replace('&amp;', '&')
        srcuid = re.search('<input type="hidden" name="srcuid" value="([^"]*)" />', res).group(1)
        rl = '1'
        req = self._process_req(urllib2.Request(addcomment_url))
        opener = urllib2.build_opener()
        data = urllib.urlencode(
                {'rl' : rl, 'srcuid' : srcuid, 'id': id, 'content' : self._unicode_encode(text)}
                )
        response = opener.open(req, data, timeout = 10)
        t = response.read()
        return '<div class="ps">评论成功!</div>' in t

if __name__ == '__main__':
    import getpass
    sina_conf = SinaWeiboWapStatus.new_channel()
    sina_conf['auth_by'] = 'userpass'
    sina_conf['channel_name'] = 'demo_channel'
    print 'Username:' ,
    sina_conf['username'] = raw_input().strip()
    sina_conf['password'] = getpass.getpass()
    sina = SinaWeiboWapStatus(sina_conf)
    print sina.auth()
    ht = sina.home_timeline(13)
    c = 0
    for i in ht:
        c += 1
        print c, i.ID.id, i.parsed.username, i.parsed.time, i.parsed.text, i.parsed.comments_count, i.parsed.reposts_count,
        if i.parsed.has_orig:
            print i.parsed.orig_text, i.parsed.orig_comments_count, i.parsed.orig_reposts_count
        else:
            print ''
