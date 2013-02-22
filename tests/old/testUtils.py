# -*- coding: utf-8 -*-

'''
Utilities for test
'''
import json
import os.path
DIR_TEST = os.path.abspath(os.path.dirname(__file__))
DIR_ROOT = os.path.dirname(DIR_TEST)
DIR_CONF = os.path.join(DIR_ROOT, "conf")
DIR_SNSAPI = os.path.join(DIR_ROOT, "snsapi")
    
def get_config_paths():
    '''
    How to get the path of config.json in test directory, Use this. 
    '''
    paths = {
            'channel': os.path.join(DIR_CONF, 'channel.json'), 
            'snsapi': os.path.join(DIR_CONF, 'snsapi.json')
            }
    return paths

def get_channel(platform):
    paths = get_config_paths()
    with open(paths['channel']) as fp:
        channel = json.load(fp)
        
    for site in channel:
        if site['platform'] == platform:
            return site
        
    raise TestInitNoSuchPlatform(platform)

def clean_saved_token():
    import os,glob
    for f in glob.glob('*.token.save'):
        os.remove(f)

class TestInitError(Exception):
    """docstring for TestInitError"""
    def __init__(self):
        super(TestInitError, self).__init__()
    def __str__(self):
        print "Test init error. You may want to check your configs."

class TestInitNoSuchPlatform(TestInitError):
    def __init__(self, platform = None):
        self.platform = platform
    def __str__(self):
        if self.platform is not None:
            print "Test init error -- No such platform : %s. " \
            "Please check your channel.json config. " % self.platform
        
if __name__ == '__main__':
    print DIR_TEST
    print DIR_ROOT
    print DIR_CONF
    print DIR_SNSAPI
    print get_config_paths()
