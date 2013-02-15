# -*- coding: utf-8 -*-

'''
Unittest for snsapi.py
the function which start with "test" will be treated as one test.
Each test start after setUp(), and end with tearDown()
'''
import sys
sys.path.append("..")
import unittest
import snsapi.snsapi as snsapi
import testUtils

class TestSnsapi(unittest.TestCase):
    def setUp(self):
        self.sns = snsapi.SNSAPI()
        
    def tearDown(self):
        self.sns = None
        
    def test_read_config(self):
        #paths = testUtils.get_config_paths()
        ##TODO only test sina is not appropriate
        ##====
        ##self.sns.platform = "sina"
        ##self.sns.read_config(pathname)
        ##====> substitute it with channel
        #self.sns.channel_name = "sina_account_1"
        #self.sns.read_config(paths['channel'])
        #self.assertIsNotNone(self.sns.channel_name)
        #self.assertIsNotNone(self.sns.platform)
        pass
        
    def test__parse_code(self):
        #sina example
        url = "http://copy.the.code.to.client/?code=b5ffaed78a284a55e81ffe142c4771d9"
        token = self.sns._parse_code(url)
        self.assertTrue(type(token.code)==str and len(token.code)>10)
        #qq example
        url = "http://copy.the.code.to.client/?code=fad92807419b5aac433c4128A05e1Cad&openid=921CFC3AF04d76FE59D98a2029D0B978&openkey=6C2FCABD153B18625BAAB1BA206EF2C6";
        token = self.sns._parse_code(url)
        self.assertTrue(type(token.code)==str and len(token.code)>10)
        self.assertTrue(type(token.openid)==str and len(token.openid)>10)

    def test_oauth2(self):
        self.sns.console_input = lambda : "http://whatever"
        self.sns.openBrower = lambda x : None
        callback_url = "http://copy.the.code.to.client/"
        auth_url = "http://whatever"
        
        with self.assertRaises(KeyError):
            self.sns.oauth2(auth_url, callback_url)
        
        
if __name__ == "__main__":
    unittest.main()
