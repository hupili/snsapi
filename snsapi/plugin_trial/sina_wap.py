#-*- encoding: utf-8 -*-

'''
Sina Weibo Wap client
'''

if __name__ == '__main__':
    import sys
    import urllib2
    import urllib
    import re
    import lxml.html, lxml.etree
    import time
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
else:
    import urllib2
    import urllib
    import re
    import lxml.html, lxml.etree
    import time
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from .. import snstype


logger.debug("%s plugged!", __file__)


class SinaWeiboWapStatusMessage(snstype.Message):
    platform = 'SinaWeiboWapStatus'
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        #TODO:
        #    Check whether the fields conform to snsapi convention.
        #    http://snsapi.ie.cuhk.edu.hk/doc/snsapi.html#module-snsapi.snstype
        self.parsed.time = dct['time']
        if u'分钟前' in self.parsed.time:
            self.parsed.time = time.time() - 60 * \
                    int(self.parsed.time[0:self.parsed.time.find(u'分钟前')])
            pp = time.localtime(self.parsed.time)
            # FIXME:
            # approximate time aligned to minute
            # if your request is at different minute from
            # the server's response. You might get ONE minute's
            # difference.
            if pp.tm_sec > 0:
                self.parsed.time = 60 + \
                        time.mktime((
                            pp.tm_year,
                            pp.tm_mon,
                            pp.tm_mday,
                            pp.tm_hour,
                            pp.tm_min,
                            0,
                            pp.tm_wday,
                            pp.tm_yday,
                            pp.tm_isdst))
        elif u'今天' in self.parsed.time:
            minute, second = map(int, re.search('([0-9]*):([0-9]*)', self.parsed.time).groups())
            today = time.gmtime(time.time() + 28800)
            self.parsed.time = time.mktime(time.strptime("%04d-%02d-%02d %02d:%02d" % (
                today.tm_year,
                today.tm_mon,
                today.tm_mday,
                minute,
                second), '%Y-%m-%d %H:%M')) - time.altzone - 28800
        else:
            minute, second = map(int, re.search('([0-9]*):([0-9]*)', self.parsed.time).groups())
            month, day = map(int, re.search(u'([0-9]*)月([0-9]*)', self.parsed.time).groups())
            today = time.gmtime(time.time() + 28800)
            self.parsed.time = time.mktime(time.strptime("%04d-%02d-%02d %02d:%02d" % (
                today.tm_year,
                month,
                day,
                minute,
                second), '%Y-%m-%d %H:%M')) - time.altzone - 28800

        self.parsed.username = dct['author']
        self.parsed.text = dct['text']
        self.parsed.comments_count = dct['comments_count']
        self.parsed.reposts_count = dct['reposts_count']
        self.parsed.userid = dct['uid']
        if 'orig' in dct:
            self.parsed.has_orig = True
            self.parsed.username_origin = dct['orig']['author']
            self.parsed.text_orig = dct['orig']['text']
            self.parsed.comments_count_orig = dct['orig']['comments_count']
            self.parsed.reposts_count_orig = dct['orig']['reposts_count']
            self.parsed.text = self.parsed.text + '//@' + self.parsed.username_origin + ':' + self.parsed.text_orig
        else:
            self.parsed.has_orig = False
        self.ID.id = dct['id']
        if 'attachment_img' in dct:
            self.parsed.attachments.append({
                'type': 'picture',
                'format': ['link'],
                'data': dct['attachment_img']
                })


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
        c['uidtype'] = 'path'
        c['auth_by'] = 'userpass'
        c['auth_info'] = {
            'save_token_file': "(default)",
            'login_username': '',
            'login_password': ''

        }
        return c

    def _process_req(self, req):
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19')
        return req


    def _get_weibo_homepage(self, token = None):
        if token:
            gsid = token['gsid']
        elif self.token and 'gsid' in self.token:
            gsid = self.token['gsid']
        else:
            gsid =  ''
        req = urllib2.Request('http://weibo.cn/?gsid=' + gsid)
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        return m

    def auth(self):
        if self.get_saved_token():
            return self.is_authed()
        if self.jsonconf['auth_by'] == 'gsid':
            self.token['gsid'] = self.jsonconf['gsid']
        elif self.jsonconf['auth_by'] == 'userpass':
            show_verification = False
            verification_code = ''
            req = urllib2.Request('http://login.weibo.cn/login/?vt=4&revalid=2&ns=1&pt=1')
            req = self._process_req(req)
            response = urllib2.urlopen(req, timeout = 10)
            p = response.read()
            while True:
                req = urllib2.Request('http://login.weibo.cn/login/?rand=' + (re.search("rand=([0-9]*)", p).group(1) )+ '&backURL=http%3A%2F%2Fweibo.cn&backTitle=%E6%89%8B%E6%9C%BA%E6%96%B0%E6%B5%AA%E7%BD%91&vt=4&revalid=2&ns=1')
                data = {'mobile': self.auth_info['login_username'],
                        'password_%s' % (re.search('name="password_([0-9]*)"', p).group(1)): self.auth_info['login_password'],
                        'backURL': 'http%3A%2F%2Fweibo.cn',
                        'backTitle': '手机新浪网',
                        'tryCount': '',
                        'vk': re.search('name="vk" value="([^"]*)"', p).group(1),
                        'submit' : '登录'}
                if show_verification:
                    data['code'] = verification_code
                    data['capId'] = re.search('name="capId" value="([^"]*)"', p).group(1)
                    show_verification = False
                req = self._process_req(req)
                data = urllib.urlencode(data)
                response = urllib2.urlopen(req, data, timeout = 10)
                p = response.read()
                final_url = response.geturl()
                if 'newlogin' in final_url:
                    final_gsid = re.search('g=([^&]*)', final_url).group(1)
                    self.token = {'gsid' :  final_gsid}
                    break
                elif '验证码' in p:
                    err_msg = re.search('class="me">([^>]*)<', p).group(1)
                    if '请输入图片中的字符' in p:
                        captcha_url = re.search(r'"([^"]*captcha[^"]*)', p).group(1)
                        show_verification = True
                        import Image
                        import StringIO
                        ss = urllib2.urlopen(captcha_url, timeout=10).read()
                        sss = StringIO.StringIO(ss)
                        img = Image.open(sss)
                        img.show()
                        verification_code = raw_input(err_msg)
                else:
                    err_msg = re.search('class="me">([^>]*)<', p).group(1)
                    logger.warning(err_msg)
                    break
        else:
            return False
        res = self.is_authed()
        if res:
            self.save_token()
        return res

    def _is_authed(self, token = None):
        '''
        ``is_authed`` is an ``SNSBase`` general method.
        It invokes platform specific ``expire_after`` to
        determine whether this platform is authed.

        Rename this method.
        '''
        return '<input type="submit" value="发布" />' in self._get_weibo_homepage(token)

    def expire_after(self, token = None):
        if self._is_authed(token):
            return -1
        else:
            return 0

    def _get_uid_by_pageurl(self, url, type='num'):
        if url[0:len('http://weibo.cn')] == 'http://weibo.cn':
            url = url[len('http://weibo.cn'):]
        if type == 'num':
            if re.search('\/u\/[0-9]*', url):
                return re.search('\/u\/([0-9]*)', url).group(1)
            req = urllib2.Request('http://weibo.cn' + url)
            req = self._process_req(req)
            m = urllib2.urlopen(req, timeout = 10).read()
            return re.search(r'\/([0-9]*)\/info', m).group(1)
        elif type == 'path':
            return re.search(r'\/([^?]*)\?', url).group(1)

    def _get_weibo(self, page = 1):
        #FIXME: 获取转发和评论数应该修改为分析DOM而不是正则表达式（以免与内容重复）
        #FIXME: 对于转发的微博，原微博信息不足
        req = urllib2.Request('http://weibo.cn/?gsid=' + self.token['gsid'] + '&page=%d' % (page))
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        h = lxml.html.fromstring(m)
        weibos = []
        for i in h.find_class('c'):
            try:
                if i.get('id') and i.get('id')[0:2] == 'M_':
                    weibo = None
                    if i.find_class('cmt'): # 转发微博
                        weibo = {
                                'uid' : self._get_uid_by_pageurl(i.find_class('nk')[0].attrib['href'], self.jsonconf['uidtype']),
                                'author' : i.find_class('nk')[0].text,
                                'id': i.get('id')[2:],
                                'time': i.find_class('ct')[0].text.encode('utf-8').strip(' ').split(' ')[0].decode('utf-8'),
                                'text' : None,
                                'orig' : {
                                    'text': unicode(i.find_class('ctt')[0].text_content()),
                                    'author': re.search(u'转发了\xa0(.*)\xa0的微博', i.find_class('cmt')[0].text_content()).group(1),
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
                            weibo['comments_count'] = int(zf.group(3))
                            weibo['reposts_count'] = int(zf.group(2))
                        zf = re.search(r'赞\[([0-9]*)\] 原文转发\[([0-9]*)\] 原文评论\[([0-9]*)\]', i.text_content().encode('utf-8'))
                        if zf:
                            weibo['orig']['comments_count'] = int(zf.group(3))
                            weibo['orig']['reposts_count'] = int(zf.group(2))
                    else:
                        weibo = {'author' : i.find_class('nk')[0].text,
                                'uid' : self._get_uid_by_pageurl(i.find_class('nk')[0].attrib['href'], self.jsonconf['uidtype']),
                                'text': i.find_class('ctt')[0].text_content()[1:],
                                'id': i.get('id')[2:],
                                'time': i.find_class('ct')[0].text.encode('utf-8').strip(' ').split(' ')[0].decode('utf-8')
                                }
                        zf = re.search(r'赞\[([0-9]*)\] 转发\[([0-9]*)\] 评论\[([0-9]*)\]', i.text_content().encode('utf-8'))
                        if zf:
                            weibo['comments_count'] = int(zf.group(3))
                            weibo['reposts_count'] = int(zf.group(2))
                    if i.find_class('ib'):
                        #FIXME: Still not able to process a collections of pictures
                        weibo['attachment_img'] = i.find_class('ib')[0].get('src').replace('wap128', 'woriginal')
                    weibos.append(weibo)
            except Exception, e:
                logger.warning("Catch exception: %s" % (str(e)))
        statuslist = snstype.MessageList()
        for i in weibos:
            statuslist.append(self.Message(i, platform = self.jsonconf['platform'],
                channel = self.jsonconf['channel_name']))
        return statuslist


    @require_authed
    def home_timeline(self, count = 20):
        all_weibo = snstype.MessageList()
        page = 1
        while len(all_weibo) < count:
            weibos = self._get_weibo(page)
            all_weibo += weibos[0:min(len(weibos), count - len(all_weibo))]
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
    try:
        # Write a 'channel.json' file in SNSAPI format with required information
        # OR, (see 'except' section)
        import json
        sina_conf = json.load(open('channel.json'))[0]
        print sina_conf
    except IOError:
        # Else, we let you input from console
        import getpass
        sina_conf = SinaWeiboWapStatus.new_channel()
        sina_conf['channel_name'] = 'demo_channel'
        sina_conf['auth_by'] = 'userpass'
        print 'Username:' ,
        _username = raw_input().strip()
        _password = getpass.getpass()
        sina_conf['auth_info'] = {
                'login_username': _username,
                'login_password': _password
                }
        sina_conf['uidtype'] = 'path'
        print sina_conf

    sina = SinaWeiboWapStatus(sina_conf)
    print sina.auth()
    # Too slow.. change the demo to 2 msgs
    ht = sina.home_timeline(2)
    #print ht
    c = 0
    for i in ht:
        c += 1
        print c, i.ID.id, i.parsed.username, i.parsed.userid, i.parsed.time, i.parsed.text, i.parsed.comments_count, i.parsed.reposts_count,
        if i.parsed.has_orig:
            print i.parsed.orig_text, i.parsed.orig_comments_count, i.parsed.orig_reposts_count
        else:
            print ''
