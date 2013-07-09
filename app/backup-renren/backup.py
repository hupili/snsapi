import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

from snsapi.snspocket import SNSPocket
sp = SNSPocket()
sp.load_config()
sp.auth()

ml = sp['myrenren'].home_timeline()
for m in ml:
    sp['mysqlite'].update(m)
