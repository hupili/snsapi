# -*- coding: utf-8 -*-

'''
Unittest for sina.py
the function which start with "test" will be treated as one test.
Each test start after setUp(), and end with tearDown().
The setUp --> test_* --> tearDown process is called Fixture.
'''
import sys
sys.path.append("..")
import unittest
import snsapi.plugin.sina as sina
import snsapi.snstype as snstype
import testUtils

class TestSina(unittest.TestCase):
    def setUp(self):
        try:
            channel = testUtils.get_channel("sina")
            self.sina = sina.SinaAPI(channel)
            self.assertIsNotNone(self.sina.app_key)
            self.assertIsNotNone(self.sina.app_secret)
        except Exception as e:
            print "Fail to initialize Sina channel. Please make sure channel.json\
                has a account on sina platform, and app_key,app_serect are valid"
            raise e;
        self.sina.auth()
        
    def tearDown(self):
        self.sina = None

    def test_auth(self):
        self.sina.auth()
        self.assertTrue(self.sina.token)
        self.assertTrue("code" in self.sina.token)
        self.assertTrue("access_token" in self.sina.token)

    def test_home_timeline(self):
        self.sina.auth()
        tls = self.sina.home_timeline(count=5)
        self.assertTrue(len(tls) == 5)
        self.assertIsInstance(tls[0], snstype.Status)
        
if __name__ == "__main__":
    unittest.main()
