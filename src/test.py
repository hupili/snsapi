# -*- coding: utf-8 -*-

import snsapi

def showStatus(ret):
    if ret == True:
        print "Success!"
        
    elif ret == False:
        print "Fail :("
        
    elif type(ret) == str:
        print ret

    elif type(ret) == dict:
        print ret

    elif type(ret) != list:
        ret.show()
    
    else:
        for s in ret:
            s.show()
            
        
if __name__ == "__main__":
    '''
    QQ weibo may fail sometimes, even with same input. May be the invoking frequency limit.
    Sina weibo is better, and more stable.
    '''
    accounts = []
    accounts.append(snsapi.sina.SinaAPI())
    accounts.append(snsapi.qq.QQAPI())
    
    for cli in accounts:
        cli.auth()
        
        print "listen first___________________________"
        sl = cli.home_timeline()
        showStatus(sl)
        
        print "update status__________________________"
        print "Input text:"
        text = raw_input()
        ret = cli.update(text)
        showStatus(ret)
    

