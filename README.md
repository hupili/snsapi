snsapi
======

跨平台，跨网站的，社交网络的中间件。
现在支持新浪微博、腾讯微博、人人网、RSS、Sqlite（试验状态）、Email（试验状态）、twitter（试验状态）。
我们的宗旨是，统一各种信息渠道的接口。

   * SNSAPI让社交网络应用程序的编写变得简单，使得一次编码就能应用于各种社交网络平台。
   * SNSAPI使得在各个平台之间传递信息变得非常方便，应用开发者可以专注于信息本身。 
   * SNSAPI支持plugin，你能很方便地利用现成的资源和模版开发其他平台的API，并无缝适用于基于SNSAPI的应用。
   * SNSAPI附带提供一个CLI，使用stdin/stdout与其他程序交互。
   不用学习Python，即可使用SNSAPI完成众多操作。

snscli上手测试
--------------

   * 首先你需要装Python2.7。
   其他兼容版本见
   [相关的wiki页面](https://github.com/hupili/snsapi/wiki/Compatibility-report)。
   * 获得该项目： 
      * 使用Git： `git clone https://github.com/hupili/snsapi.git`。 
      * 或直接下载zip包： [https://github.com/hupili/snsapi/zipball/master](https://github.com/hupili/snsapi/zipball/master)
      * (大陆用户：如果上面链接无法取得项目源码，请尝试将`https`改为`http`）
   * 安装依赖库：`[sudo] pip install -r requirements.txt`。
   * 进入项目根目录，`python -i snscli.py`。

我们在`snscli.py`中集成完整的教程，
将带你了解SNSAPI的基本操作。
可以使用`print helpdoc`随时开启帮助菜单。
可以使用`print tut`浏览教程。
你将在10分钟之内体验到SNSAPI的基本功能，
以及便利的跨平台信息收发。

如遇到中文乱码，请参考“编码问题”章节。

以下将包含一些交互运行中的片段，希望能让大家对snscli有个大致印象。
（人人的信息被打码了）

```
>>> auth()
[INFO][20120911-163533]Read saved token for 'sina_account_1' successfully
[INFO][20120911-163533]Read saved token for 'qq_account_1' successfully
[INFO][20120911-163533]Read saved token for 'renren_account_1' successfully
>>> sl = home_timeline(2)
[INFO][20120911-163552]Read 2 statuses from 'renren_account_1'
[INFO][20120911-163552]Read 6 statuses
>>> print sl
[创意铺子] at Tue Sep 11 16:30:10 +0800 2012 
  女孩纸们看看哪款香水适合你？
[百度开发者中心] at Tue Sep 11 16:27:57 +0800 2012 
  百度技术沙龙第三十期：网页展示新技术实践（9月15日 周六）http://t.cn/zWgpOhE
[wj_xlt] at 1347351357 
  【外交掠影】9月7日，中国新任驻乍得大使胡志强在乍得总统府向乍总统代比递交国书。代比总统对胡大使履新表示欢迎，并希望乍中双方进一步丰富合作内涵，推动更多中国企业在乍发展。<a href="http://url.cn/519bG3" target="_blank">http://url.cn/519bG3</a> 
[xylzx2011] at 1347350990 
  【那英合肥“惊艳”开唱 甘当绿叶几度哽咽】9月8日晚，歌坛天后@那英 来到合肥举办个人演唱会，当天那英一改往日形象，带着金色假发、穿着透视装登台。演唱会当晚合肥正下着大雨，但这并没有减低歌迷们的热情。现场座无虚席，歌迷们更是一起随着音乐挥舞着荧光棒。 <a href="http://url.cn/6iafBP" target="_blank">http://url.cn/6iafBP</a> 
[xxx] at 2012-09-11 13:53:58 
  xxx
[xxx] at 2012-09-11 13:37:43 
  xxx
>>> update("test", channel = "sina_account_1")
[INFO][20120911-163946]Update status 'test'. Result:{'sina_account_1': True}
{'sina_account_1': True}
>>> sl = home_timeline(2, channel = "sina_account_1")
[INFO][20120911-164017]Read 2 statuses
>>> print sl
[snsapi_test] at Tue Sep 11 16:39:46 +0800 2012 
  test
[百度] at Tue Sep 11 16:38:34 +0800 2012 
  实用！把iphone调的比最大声音还大的方法[赞]
>>> save_config()
[INFO][20120911-164515]save configs done
>>> quit()
```

还等什么？赶快开启snscli的教程吧。

stdin/stdout测试
----------------

下面这行linux命令将向你展示snsapi的stdin/stdout接口。

```
$echo -e 'load_config()\nauth()\nprint home_timeline(10)' | python -i snscli.py -c | grep "snsapi_test" -A 1
>>> [INFO][20120911-165746]Read configs done. Add 1 channels
>>> [INFO][20120911-165746]Read saved token for 'sina_account_1' successfully
>>> [INFO][20120911-165748]Read 10 statuses
>>> 
[snsapi_test] at Tue Sep 11 16:39:46 +0800 2012 
  test
```

在新浪微波上关注`snsapi_test`，然后运行这个命令。
如果前10条消息中，有`snsapi_test`发的，你将能把它grep出来。
你完全可以用脚本实现更复杂的功能，
通过stdin对snscli输入命令，并从stdout得到结果。
你可以定制自己的过滤规则、转发规则，等等。


编码问题
--------

整个工程是使用utf-8编码的。
SNSAPI默认使用utf-8读写外部数据，
在SNSAPI内部统一使用unicode。
如果在中文系统下运行出编码问题，
请打开snsapi/snsconf.py，把最后一行的

```
SNSAPI_CONSOLE_STDOUT_ENCODING = 'utf-8'
```

更改为（比如你系统使用的是gbk）

```
SNSAPI_CONSOLE_STDOUT_ENCODING = 'gbk'
```
    
应用
----

基础应用:

   * hellosns: 
   [https://github.com/hupili/snsapi/tree/master/app/hellosns](https://github.com/hupili/snsapi/tree/master/app/hellosns).
   hello SNS将向你展示怎样用10行代码完成与SNS交互的基本功能，
   它就是利用SNSAPI开发app的hello world啦。
   * clock: 
   [https://github.com/hupili/snsapi/tree/master/app/clock](https://github.com/hupili/snsapi/tree/master/app/clock).
   clock是一口SNS平台上的钟，你可以很方便的用它来定时发布消息。
   * forwarder: 
   [https://github.com/hupili/snsapi/tree/master/app/forwarder](https://github.com/hupili/snsapi/tree/master/app/forwarder).
   forwarder可以把一个平台的信息自动地发送到其他
   平台，你需要做地只是填写配置文件，告诉它接收哪个平台信息，发布到哪些平台上。
   * mysofa: 
   [https://github.com/hupili/snsapi/tree/master/app/mysofa](https://github.com/hupili/snsapi/tree/master/app/mysofa).
   mysofa我想你已经猜到了，就是用来抢沙发的 :D

进阶应用:

   * SNSRouter:
   [https://github.com/hupili/sns-router](https://github.com/hupili/sns-router). 
   正如其名，这个app将构建跨平台的智能存档、转发系统。
   它目前还在活跃的开发阶段。

trial状态的插件
---------------

SNSAPI中会不断加入新的插件。
标准插件会所需的代码会包含在项目中，打包下载即可使用。
如果需要使用trial状态的插件，你可能需要先更新依赖关系的项目。

切换到snsapi的根目录下：

```
git submodule init
git submodule update
```

开启和关闭trial插件请见`snsapi/platform.py`，
选择注释是否`import`他们即可。

后记
----

如果你不了解geek的世界，我能理解你看到一个
没有图形界面、充斥各种代码和术语的软件，
是多么的糟糕和令你困惑，
但如果你想很快地实践自己对社交网络的一些新奇想法，入手snsapi吧！

项目还在成长，所以还有很多考虑不到的东西请多包涵，
也请给我们多提建议，更加欢迎你能参与进来，与我们一起改造社交网络！

资源
----

   * [SNSAPI官网](http://snsapi.ie.cuhk.edu.hk/)。
   目前由hupili维护，如果发现问题，请通知管理员。
   也欢迎直接发patch到[repo](https://github.com/hupili/snsapi-website)。
   * [SNSAPI中文网](http://snsapi.sinaapp.com/)。
   目前由xuanqinanhai维护。
   * [SNSAPI文档](https://snsapi.ie.cuhk.edu.hk/doc/)。
   用Sphinx从Python代码直接生成的Doc。
   也可以在使用SNSAPI的过程中，通过`help(XXX)`唤出。
   * [SNSAPI Github Wiki](https://github.com/hupili/snsapi/wiki)，
   所有github用户均可进行编辑，欢迎分享你的经验！
   * [SNSAPI Google Group](https://groups.google.com/forum/?fromgroups#!forum/snsapi)
   请加入这个社区，一同推进SNSAPI，我们会及时解决你遇到的各种问题。

Copy Left
---------

![copyleft](http://unlicense.org/pd-icon.png)

[http://unlicense.org](http://unlicense.org)

All files of this project are released to public domain,
except for the followings:

   * `snsapi/third/*`: The third party modules. 
   Please refer to their original LICENSE. 
   We have pointers in `snsapi/third/README.md`
   for those third party modules. 
