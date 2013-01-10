# -*- coding: utf-8 -*-

from snsapi.snspocket import SNSPocket
from datetime import datetime
import time

TEXTS = ['凌晨好', '清晨好', '早上好', '下午好', '傍晚好', '晚上好']
#URL = 'https://github.com/hupili/snsapi/tree/master/app/clock'
URL = 'http://t.cn/zj1VSdV'
AD = '10行写个跨平台的钟：%s' % URL

sp = SNSPocket() # SNSPocket 是一个承载各种SNS的容器
sp.load_config() # 如名
sp.auth()        # 批量授权（如果已授权，读取授权信息）

while True: 
    h, m = datetime.now().hour, datetime.now().minute                        # 获取当前小时和分钟
    if m == 0:                                                               # 每小时0分钟的时候发状态
        t = '%s -- 0x%X点钟， %s。( %s )' % ('烫' * h, h, TEXTS[h / 4], AD)  # 构造钟的报时文字
        print t
        sp.update(t)                                                         # 发一条新状态
    time.sleep(60)                                                           # 睡一分钟
