# -*- coding: utf-8 -*-

'''
Test utilities
'''
    
    
def get_config_path():
    '''
    How to get the path of config.json in test directory, Use this. 
    '''
    import os.path
    #make the pathname of config.json
    pathname = os.path.abspath("conf/config.json")
    pathname = pathname.replace('test/', "")
    pathname = pathname.replace('test\\', "")
    return pathname