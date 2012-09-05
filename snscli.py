# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json
from os.path import abspath

from snsapi.utils import JsonDict
from snsapi.snspocket import SNSPocket
sp = SNSPocket()

read_config = lambda *al, **ad : sp.read_config(*al, **ad)
save_config = lambda *al, **ad  : sp.save_config(*al, **ad)
list = lambda  *al, **ad : sp.list(*al, **ad)
auth = lambda  *al, **ad : sp.auth(*al, **ad)
home_timeline = lambda *al, **ad : sp.home_timeline(*al, **ad)
update = lambda  *al, **ad : sp.update(*al, **ad)
reply = lambda  *al, **ad : sp.reply(*al, **ad)
new_channel = lambda : JsonDict(json.load(open(abspath('conf/init-channel.json.example'),'r')))

#==== default initialization one may like ====

#read_config()
#list()
#auth()
