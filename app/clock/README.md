# 怎么写一个钟？

## 步骤

   * 先去
   [新浪开放平台](http://open.weibo.com/development)
   注册开发者、注册应用、得到`app_key`和`app_secret`、
   填写`call_backurl`
   （随便填一个供新浪准许的url就可以，或者参考之后`channel.json`里面的`callback_url`）。
   * 下载
   [snsapi](https://github.com/hupili/snsapi/)。
   可以`git clone`，也可以直接下载
   [zip打包](https://github.com/hupili/snsapi/archive/master.zip)。
   * 填写`channel.json`配置文件（后有样例），
   这样就开启新浪微博这个通道了
   （之后要支持其他平台，也就是注册app和填写`channel.json`而已）。
   * 写clock的逻辑：
   先准备语料；
   然后“发状态--睡一小时--发状态--睡一小时”循环。
   详情见`clock.py`。
   * 将`clock.py`放入`snsapi`的根目录下执行。

*注意：*
第一次运行的时候，
请按照console上的提示完成授权流程；
snsapi默认会将授权信息记录在本地`*.save`中，
之后调用会自动读取（可配置不保存）。
（详情请参考后面“授权流程”）

## `channel.json` 配置文件样例

我们在`conf`下放有各种`*.example`文件，包括channel。
对于这个clock程序，可以改写下面这个文件即可。

```
[
  {
    "platform": "SinaWeiboStatus", 
    "methods": "home_timeline,update,forward",
    "user_id": "可以不填", 
    "user_name": "可以不填",
    "channel_name": "sina_account_1", 
    "auth_info": {
      "save_token_file": "(default)", 
      "callback_url": "https://snsapi.ie.cuhk.edu.hk/aux/bouncer/redir/localhost/11111/", 
      "cmd_fetch_code": "(console_input)", 
      "cmd_request_url": "(console_output)"
    }, 
    "app_key": "填写你在开放平台上的app_key", 
    "app_secret": "填写你在开放平台上的app_secret", 
    "open": "yes", 
    "home_timeline":{
      "count": 100
    }
  } 
]
```

注意：`callback_url`必须和你在“开放平台--应用信息--高级信息--OAuth2.0”处填写的一致。

## 授权流程

当`channel.json`配置好后，可以当即使用`snscli`进行简单测试
（可以略过这节，直接跑`clock.py`，授权流程是一样的；
使用`snscli`测试是因为这个脚本提供更多的功能）。

执行`python -i snscli.py`：
（“# xxxx”是注释）

```
# 略过一些输出
https://api.weibo.com/oauth2/authorize?redirect_uri=https%3A//snsapi.ie.cuhk.edu.hk/aux/bouncer/redir/localhost/11111/&response_type=code&client_id=这里会显示你注册的app_key&display=json
# 用浏览器访问上面的网址。
# 完成授权后会重定向到你之前设置的callback_url。
# 复制地址栏中的url到控制台，如下所示，
Please input the whole url from Broswer's address bar:
# 下面这行就是从浏览器中复制过来的，复制后回车。
http://localhost:11111/auth/second/?code=b5ae这里是一串授权代码c827db
# 略过一些输出，当你看到下面这行的时候，表示授权成功了！！！！
[INFO][20130110-143254][snsbase.py][_oauth2_second][176]Channel 'sina_account_1' is authorized
# 现在测试下得到自己的timeline上的一条新信息，如下
>>> print ht(1)
[INFO][20130110-143259][snspocket.py][home_timeline][254]Read 1 statuses
<0>
[程序媛念茜] at Thu, 10 Jan 2013 14:32:45 HKT 
  已请辞CSDN论坛Android版块版主、Qt版块版主职务，感谢大家一直以来的支持和配合，最大的收获就是认识了一大帮新朋友，我就不一个一个@了，咱群里喷。如今实在分身乏术，时间精力有限，绝不是因为我爱上iOS了。今后也想多些时间陪陪父母。嗯，卸甲归田了，妥妥的。
```

## 扩展

这只是一个proof of concept:

   * 编写更复杂的钟逻辑。
   写好后我可以把链接加在这里，
   方便他人寻找更多的样例。
   * 去[snsapi网站](https://snsapi.ie.cuhk.edu.hk/)
   阅读snsapi入门材料。
   * 遇到问题？发
   [issue](https://github.com/hupili/snsapi/issues?state=open)。
   有经验想分享？写
   [wiki](https://github.com/hupili/snsapi/wiki)。

