# -*- coding: utf-8 -*-

'''
Utilities for test
'''
import json
    
def get_config_path():
    '''
    How to get the path of config.json in test directory, Use this. 
    '''
    import os.path
    #make the pathname of config.json
    #pathname = os.path.abspath("conf/config.json")
    pathname = os.path.abspath("conf/channel.json")
    pathname = pathname.replace('test/', "")
    pathname = pathname.replace('test\\', "")
    return pathname

def get_channel(platform):
    path = get_config_path()
    with open(path) as fp:
        channel = json.load(fp)
        
    for site in channel:
        if site['platform'] == platform:
            return site
        
    return None

def clean_saved_token():
    import os,glob
    for f in glob.glob('*.token.save'):
        os.remove(f)