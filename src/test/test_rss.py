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
import snsapi.plugin.rss as rss
import snsapi.snstype as snstype
import testUtils

class TestSina(unittest.TestCase):
    def setUp(self):
        try:
            channel = testUtils.get_channel("rss")
            self.rss = rss.RSSAPI(channel)
            self.assertIsNotNone(self.rss.url)
        except Exception as e:
            print "Fail to initialize RSS channel. Please make sure channel.json\
                has an entry for RSS platform, and it has 'url' field"
            raise e;
        self.rss.auth()
        
    def tearDown(self):
        self.rss = None

    def test_home_timeline(self):
        tls = self.rss.home_timeline(count=5)
        self.assertTrue(len(tls) == 5)
        self.assertIsInstance(tls[0], snstype.Status)
        
if __name__ == "__main__":
    unittest.main()
