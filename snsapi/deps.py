# -*- coding: utf-8 -*-

import sys
import os
_path_me = os.path.abspath(__file__)
_path_snsapi = os.path.dirname(_path_me)
_path_third = os.path.join(_path_snsapi, 'third')

sys.path.append(_path_snsapi)
sys.path.append(_path_third)

if __name__ == '__main__':
    print _path_me
    print _path_snsapi
    print _path_third
