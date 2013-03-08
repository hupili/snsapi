#-*- encoding: utf-8 -*-

'''
Sina Weibo client
'''

if __name__ == '__main__':
    import sys
    import urllib2
    import urllib
    import re
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
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from .. import snstype
    from ..utils import console_output
    from .. import utils


logger.debug("%s plugged!", __file__)


class SinaWeiboWapStatus:
    def __init__(self, conf):
        assert conf['auth_by'] in ['userpass', 'gsid']
        self.conf = conf


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
        req = urllib2.Request('http://weibo.cn/?gsid=' + self.gsid)
        req = self._process_req(req)
        m = urllib2.urlopen(req, timeout = 10).read()
        return m

    def auth(self):
        if self.conf['auth_by'] == 'gsid':
            self.gsid = self.conf['gsid']
        elif self.conf['auth_by'] == 'userpass':
            req = urllib2.Request('http://weibo.cn/dpool/ttt/login.php')
            req = self._process_req(req)
            data = {'uname' : self.conf['username'], 'pwd': self.conf['password'],
                    'l' : '', 'scookie' : 'on', 'submit' : '登录'}
            data = urllib.urlencode(data)
            response = urllib2.urlopen(req, data, timeout = 10)
            p = response.read()
            final_url = response.geturl()
            self.gsid = final_url[final_url.find('=') + 1:]
        else:
            return False
        return self.is_authed()

    def is_authed(self):
        return '<input type="submit" value="发布" />' in self._get_weibo_homepage()

    @require_authed
    def home_timeline(self, number):
        pass

    @require_authed
    def update(self, text):
        homepage = self._get_weibo_homepage()
        m = re.search('<form action="(/mblog/sendmblog?[^"]*)" accept-charset="UTF-8" method="post">', homepage).group(1)
        data = {'rl' : '0', 'content' : text}
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
        url = 'http://weibo.cn/comment/%s?gsid=%s' % (id, self.gsid)
        req = self._process_req(urllib2.Request(url))
        res = urllib2.build_opener().open(req, timeout = 10).read()
        addcomment_url = 'http://weibo.cn' +  \
                re.search('<form action="(/comments/addcomment?[^"]*)" method="post">', res).group(1).replace('&amp;', '&')
        srcuid = re.search('<input type="hidden" name="srcuid" value="([^"]*)" />', res).group(1)
        rl = '1'
        req = self._process_req(urllib2.Request(addcomment_url))
        opener = urllib2.build_opener()
        data = urllib.urlencode(
                {'rl' : rl, 'srcuid' : srcuid, 'id': id, 'content' : text}
                )
        response = opener.open(req, data, timeout = 10)
        t = response.read()
        return '<div class="ps">评论成功!</div>' in t

if __name__ == '__main__':
    import getpass
    sina_conf = SinaWeiboWapStatus.new_channel()
    sina_conf['auth_by'] = 'userpass'
    print 'Username:' ,
    sina_conf['username'] = raw_input().strip()
    sina_conf['password'] = getpass.getpass()
    sina = SinaWeiboWapStatus(sina_conf)
    print sina.auth()
