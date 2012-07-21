# -*- coding: utf-8 -*-

'''
Unittest for qq.py
the function which start with "test" will be treated as one test.
Each test start after setUp(), and end with tearDown()
'''
import sys
sys.path.append("..")
import unittest
import snsapi.plugin.sina as sina
import snsapi.snstype as snstype
import testUtils

class TestSina(unittest.TestCase):
    def setUp(self):
        f = sina.SinaAPI.read_config
        sina.SinaAPI.read_config = lambda x : f(x,testUtils.get_config_path())
        self.sina = sina.SinaAPI()
        self.sina.channel_name = "sina_account_1"

        self.sina.read_config()
        self.assertIsNotNone(self.sina.app_key)
        self.assertIsNotNone(self.sina.app_secret)
        self.sina.auth()
        
    def tearDown(self):
        self.sina = None

    #def test_read_config(self):
    #    self.sian.read_config()
    #    self.assertIsNotNone(self.sina.app_key)
    #    self.assertIsNotNone(self.sina.app_secret)

    #def test_auth(self):
    #    self.sina.auth()

    def test_home_timeline(self):
        tls = self.sina.home_timeline(count=5)
        self.assertTrue(len(tls) == 5)
        self.assertIsInstance(tls[0], snstype.Status)
        
if __name__ == "__main__":
    unittest.main()
