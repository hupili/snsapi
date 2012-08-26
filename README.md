snsapi
======

跨平台，跨网站的，社交网络的python API。现在支持新浪微博、腾讯微博、人人网和rss。
我们的宗旨是，让社交网络应用程序的编写变得简单，使得一次编码就能应用于各种社交网络平台，
让各个平台的信息更方便地传播到另一个之中。我们在snsapi的结构中引入了plugin的想法，你能很方便地
利用现成的资源和模版开发其他平台的python API，并与现有的平台同构！

如果你不了解geek的世界，我能理解你看到一个没有图形界面，充斥各种代码和术语的软件，是多么的糟糕
和令你困惑，但如果你想很快地实践自己对社交网络的一些新奇想法，入手snsapi吧！

项目还在成长，所以还有很多考虑不到的东西请多包涵，也请给我们多提建议，更加欢迎你能参与进来，与我们
一起改造社交网络！

上手小测试：
----

首先配置你的APP_KEY和APP_SECRET：
把conf/channel.json.example复制并重命名为channel.json(必须一字不差)，在该文件中里面填写你的
platform(sina、qq、renren或rss), app_key 和 app_secret

然后执行程序：
cd SNSAPI_ROOT，
python test-read-all.py。
之后会弹出网页，填入账号密码后点授权，接着从跳转的页面的地址栏里复制出url，填入console(cmd)窗口中，
应该就能得到home_timeline了。good luck。

另外：整个工程使用utf-8编码的，所以如果在windows的cmd窗口中运行程序可能出现编码问题，
若如此，打开snsapi/snsconf.py，把最后一行的
    SNSAPI_CONSOLE_STDOUT_ENCODING = 'utf-8'
更改为
    SNSAPI_CONSOLE_STDOUT_ENCODING = 'gbk'
    
APP:
----

在app目录中沉睡着两个有趣的应用，forwarder和mysofa，forwarder可以把一个平台的信息自动地发送到其他
平台，你需要做地只是填写配置文件，告诉它接收哪个平台信息，发布到哪些平台上。mysofa我想你已经猜到了，
就是用来抢沙发的 :D
更详细的使用方法请vim app/forwarder/README.md