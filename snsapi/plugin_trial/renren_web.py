#-*- encoding: utf-8 -*-

'''
Renren Web Interface 

Depends on xiaohuangji interfaces
'''

if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from snslog import SNSLog as logger
    from snsbase import SNSBase, require_authed
    import snstype
    from utils import console_output
    import utils
else:
    import sys
    from ..snslog import SNSLog as logger
    from ..snsbase import SNSBase, require_authed
    from .. import snstype
    from ..utils import console_output
    from .. import utils

from os.path import abspath, join, dirname
__DIR_ME = abspath(__file__)
__DIR_THIRD = join(dirname(dirname(__DIR_ME)), 'third')
sys.path.append(__DIR_THIRD)
from xiaohuangji.renren import RenRen as RenrenXiaohuangjiInt

logger.debug("%s plugged!", __file__)

if __name__ == '__main__':
    try:
        from my_accounts import accounts
    except:
        print "please configure your renren account in 'my_account.py' first"
        sys.exit(-1)
    renren = RenrenXiaohuangjiInt()
    renren.login(accounts[0][0], accounts[0][1])
    print renren.info

