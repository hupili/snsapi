#-*- encoding: utf-8 -*-

'''
Github client
'''

#system libs
import urllib2
import urllib
#end system libs
from ..utils import json
from ..snslog import SNSLog as logger 
from ..snsbase import SNSBase, require_authed
from .. import snstype
from ..errors import snserror
from .. import utils

'''
	Not completely supporting, because it has too much work ..... 
	It's a good example of how to auth and using Github api
	I'll try to add more support on this
	2013-1-28 12:38
'''

logger.debug("%s plugged!", __file__)

GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

personal_info_zn_map = {
	"login":"用户名:{0}",
	"created_at":"账户创建时间:{0}",
	"avatar_url":"头像地址:{0}",
	"updated_at":"上次活动:{0}",
	"following":"追随了:{0}人",
	"public_repos":"公开Repos:{0}个",
	"html_url":"主页地址:{0}",
	"starred_url":"加星列表:{0}",
	"repos_url":"Repo地址：{0}",
	"followers_url":"追随人列表：{0}",

}

class GithubStatusMessage(snstype.Message):
	platform = "GithubStatus"
	def parse(self):
		pass

class GithubStatus(SNSBase):

	Message = GithubStatusMessage

	def __init__(self, channel = None):
		super(GithubStatus, self).__init__(channel)

		self.platform = self.__class__.__name__
		self.Message.platform = self.platform

	@staticmethod
	def new_channel(full = False):
		c = SNSBase.new_channel(full)

		c['app_key'] = ''
		c['app_secret'] = ''
		c['platform'] = 'GithubStatus'
		c['auth_info'] = {
						"save_token_file":"(default)",
						"cmd_request_url":"(default)",
						"cmd_fetch_code":"(default)",
						"auth_url":"https://github.com/login/oauth/"
						}

		return c

	def read_channel(self, channel):
		super(GithubStatus,self).read_channel(channel)
		if not "auth_url" in self.auth_info:
			self.auth_info.auth_url = "https://github.com/login/oauth/"

	def need_auth(self):
		return True

	def auth_first(self):
		self._oauth2_first()

	def auth_second(self):
		try:
			url = self.fetch_code()
			self.token = self.parseCode(url)
			logger.info("Url %s",url)
			args = dict(url="",client_id=self.jsonconf.app_key,redirect_uri = self.auth_info.callback_url,client_secret=self.jsonconf.app_secret)
			args["code"] = self.token.code
			logger.info("args information %s",args)
			self.token.update(self._http_post(GITHUB_ACCESS_TOKEN_URL, args))
			
		except Exception,e:
			logger.warning("Auth second fail. Catch Exception %s",e)
			token = None

	def auth(self):
		if self.get_saved_token():
			return
		logger.info("Try to authenticate github channel: '%s' using OAuth2", self.jsonconf.channel_name)
		self.auth_first()
		self.auth_second()
		logger.debug("Authorized! access token is " + str(self.token))
		logger.info("Channel '%s' is authorized", self.jsonconf.channel_name)

	def _http_post(self, baseurl, params):

		logger.info("BaseUrl:%s params:%s",baseurl,params)

		try:
			for p in params:
				params[p] = self._unicode_encode(params[p])
			req = urllib2.Request(baseurl)
			req.add_header("Accept","application/json")
			data = urllib.urlencode(params)
			req.add_data(data)
			resp = urllib2.urlopen(req)
			json_objs = json.loads(resp.read())
			return json_objs
		except Exception ,e:
			logger.warning("_http_post fail: %s",e)
			return {}

	def __get_json(self,url):
		try:
			f = urllib2.urlopen(url)
			return json.loads(f.read())
		except Exception,e:
			logger.debug("%s",e)
			exit()

	def get_personnal_info(self):
		'''
		after get access_token,you can using token to get User Information
		GET https://api.github.com/user?access_token=...
		Json response

		return:
			json
		'''
		logger.info("start getting personal inforamtion using token\n")
		try:
			f = urllib2.urlopen("https://api.github.com/user?access_token=%s"%self.token['access_token'])
			self.personal_info = json.loads(f.read())
			return self.personal_info
		except Exception,e:
			logger.debug("%s",e)
			exit()

	def get_personnal_stared(self):
		'''
		after get access_token,you can using this function to get a json stars list
		'''
		addresss = self.personal_info['starred_url'][0:-15]
		logger.info("staring fetch starts from:%s",addresss)
		return self.__get_json(addresss)	

	def get_personnal_following(self):
		'''
		get all followers inforamtion
		'''
		addresss = self.personal_info["following_url"]
		logger.info("starting fetch followers form:%s",addresss)
		return self.__get_json(addresss)
			
	#...........you can do more from offical doc.............#

	#........................................................#


##——————————————below are test functions , you can delete——————————————————##

	def prepare_data(self):

		if hasattr(self,"personal_info") == False:
			self.get_personnal_info()

	def test_show_personnal_info(self):
		'''
			show github user information.
		'''
		#This is just a simple function to test if it works
		#You can do more on this
		self.prepare_data()
		#logger.info("%s",json.dumps(self.personal_info, indent=8)) 
		for k in self.personal_info:
			if k in personal_info_zn_map:
				print personal_info_zn_map[k].format(self.personal_info[k])

			
	def test_show_stars(self):
		'''
			show all the projects that user stared
		'''
		#just a test of ,you can modify the output format by yourself
		self.prepare_data()
		stars = self.get_personnal_stared()
		#logger.info(json.dumps(stars,indent=8))
		print "What I starred:\n"
		for s in stars:
			print "PROJECT:",s["full_name"],"HOMEPAGE:",s['homepage'],"\n"

	def test_show_following(self):
		self.prepare_data()
		followers = self.get_personnal_following()

		print "Who I am following:\n"
		for s in followers:
			print 'Name:',s['login'],"\n"
##——————————————end test function——————————————————##




	


















