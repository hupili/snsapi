# -*- coding: utf-8 -*-

'''
Unittest for renren.py
the function which start with "test" will be treated as one test.
Each test start after setUp(), and end with tearDown().
The setUp --> test_* --> tearDown process is called Fixture.
'''
import sys
sys.path.append("..")
import unittest
import snsapi.plugin.renren as renren
import snsapi.snstype as snstype
import testUtils

class TestRenren(unittest.TestCase):
    def setUp(self):
        try:
            channel = testUtils.get_channel("renren")
            self.renren = renren.RenrenAPI(channel)
            self.assertIsNotNone(self.renren.app_key)
            self.assertIsNotNone(self.renren.app_secret)
        except Exception as e:
            print "Fail to initialize Renren channel. Please make sure channel.json\
                has an account on renren platform, and app_key,app_serect are valid"
            raise e;
        
    def tearDown(self):
        self.renren = None

    def test_auth(self):
        self.renren.auth()
        self.assertTrue(self.renren.token)
        self.assertTrue("code" in self.renren.token)
        self.assertTrue("access_token" in self.renren.token)

    def test_home_timeline(self):
        self.renren.auth()
        tls = self.renren.home_timeline(count=5)
        self.assertTrue(len(tls) == 5)
        self.assertIsInstance(tls[0], snstype.Status)
        
if __name__ == "__main__":
    unittest.main()
