# -*- coding: utf-8 -*-

'''
Unittest for qq.py
the function which start with "test" will be treated as one test.
Each test start after setUp(), and end with tearDown()
'''
import sys
sys.path.append("..")
import unittest
import snsapi.plugin.qq as qq
import snsapi.snstype as snstype
import testUtils

class TestQQ(unittest.TestCase):
    def setUp(self):
        try:
            channel = testUtils.get_channel("qq")
            self.qq = qq.QQAPI(channel)
            self.assertIsNotNone(self.qq.app_key)
            self.assertIsNotNone(self.qq.app_secret)
        except Exception as e:
            print "Fail to initialize Sina channel. Please make sure channel.json\
                has a account on qq platform, and app_key,app_serect are valid"
            raise e;
        
    def tearDown(self):
        self.qq = None

    def test_auth(self):
        self.qq.auth()
        self.assertTrue(self.qq.token)
        self.assertTrue("code" in self.qq.token)
        self.assertTrue("access_token" in self.qq.token)

    def test_home_timeline(self):
        self.qq.auth()
        tls = self.qq.home_timeline(count=5)
        self.assertTrue(len(tls) == 5)
        self.assertIsInstance(tls[0], snstype.Status)
        
if __name__ == "__main__":
    unittest.main()
