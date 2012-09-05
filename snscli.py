# -*- coding: utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json
from os.path import abspath

from snsapi.utils import JsonDict
from snsapi.utils import console_output, console_input
from snsapi.snspocket import SNSPocket

sp = SNSPocket()

read_config = lambda *al, **ad : sp.read_config(*al, **ad)
save_config = lambda *al, **ad  : sp.save_config(*al, **ad)
list_channel = lambda  *al, **ad : sp.list_channel(*al, **ad)
auth = lambda  *al, **ad : sp.auth(*al, **ad)
home_timeline = lambda *al, **ad : sp.home_timeline(*al, **ad)
update = lambda  *al, **ad : sp.update(*al, **ad)
reply = lambda  *al, **ad : sp.reply(*al, **ad)
new_channel = lambda : JsonDict(json.load(open(abspath('conf/init-channel.json.example'),'r')))

#==== documentation ====

helpdoc = \
"""
snscli -- the interactive CLI to operate all SNS!

Type "print helpdoc" again to see this document. 

To start your new journey, type "print tut"

Here's the command list:
   * read_config 
   * save_config 
   * list 
   * auth 
   * home_timeline 
   * update 
   * reply 
   * new_channel 
"""

class SNSAPITutorial(object):
    """docstring for SNSAPITutorial"""
    def __init__(self):
        super(SNSAPITutorial, self).__init__()
        self.pointer = -1 
        self.sections = []

        self.sections.append(""" 
Section 0. 
    To navigate this tutorial, you need:
       * tut.next() : move to next section
       * tut.prev() : move to previous section
    Note that "print tut" is the shortcut
    to move to the next section. 
        """)

        self.sections.append(""" 
Section 1. 
        """)

        self.sections.append("""
Section 2.
        """)

        self.sections.append("""
Section 3.
        """)

    def next(self):
        self.pointer += 1
        tut = self.sections[self.pointer % len(self.sections)]
        console_output(tut)

    def prev(self):
        self.pointer -= 1
        tut = self.sections[self.pointer % len(self.sections)]
        console_output(tut)

    def __str__(self):
        self.pointer += 1
        tut = self.sections[self.pointer % len(self.sections)]
        return tut

tut = SNSAPITutorial()
        

#==== default initialization one may like ====

print helpdoc
#read_config()
#list()
#auth()
