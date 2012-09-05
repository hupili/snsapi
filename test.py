from snsapi.snspocket import SNSPocket
from snsapi.utils import console_input,console_output

sp = SNSPocket()
sp.read_config()

#======= test iter dict ====

for cname in sp:
    print cname

#s.list(verbose = True)
sp.list()
sp.auth()

#======= print statuses =====
s_list = sp.home_timeline()
#for s in s_list:
#    print unicode(s)
#print unicode(s_list)
#print str(s_list)
print s_list

#======= update status =====
#print "input something to update:==="
#s.update(console_input())

#======= reply status ====
#sp.reply(s_list[0].ID, 'haha')

