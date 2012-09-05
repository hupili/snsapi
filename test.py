

from snsapi.snspocket import SNSPocket

s = SNSPocket()
s.read_config()
#s.list(verbose = True)
s.list()
s.auth()
s_list = s.home_timeline()
#for s in s_list:
#    print unicode(s)
#print unicode(s_list)
#print str(s_list)
print s_list

