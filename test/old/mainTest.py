# -*- coding: utf-8 -*-

'''
Test portal.
Run this script to full test.
TestSuite is the top level of this test framework.
TestSuite <-- TestCase <-- Fixture
If you want to know more about the test framework for Python, read following web pages.
http://www.voidspace.org.uk/python/articles/introduction-to-unittest.shtml
http://docs.python.org/library/unittest.html
'''

import test_snsapi,test_sina,test_qq,test_rss,test_renren
import unittest
import testUtils

def suite():
    suite = unittest.TestSuite()
    #suite.addTest(test_snsapi.TestSnsapi())
    suite.addTest(test_sina.TestSina("test_auth"))
    suite.addTest(test_sina.TestSina("test_home_timeline"))
    suite.addTest(test_qq.TestQQ("test_auth"))
    suite.addTest(test_qq.TestQQ("test_home_timeline"))
    return suite;
    
if __name__ == "__main__":
    sut = suite()
    
    runner = unittest.TextTestRunner();
    runner.run(sut)
    '''
    Or, If you want to save the test result. You can try:
    result = unittest.TestResult()
    sut.run( result )
    print result
    '''
    
    #clean up
    testUtils.clean_saved_token()
