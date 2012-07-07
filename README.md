snsapi
======

for Chinese
跨平台，跨网站的，社交网络的python API。刚开始只支持新浪微博和腾讯微博。

本人对自己能否写出漂亮的代码不是很有信心，如果您能给我提建议，我将非常珍惜，谢谢！

在Python2.7上开发的。
使用Eclipse + PyDev开发，所以你会在根目录下看到一堆.settings,.project什么的。
直接在Eclipse中import Existing Projects into Workspace就能打开工程。
安装Eclipse的PyDev插件请参照http://pydev.org/download.html，
安装好记得配置Interpreter:Window->Preferences->PyDev->Interpreter-Python->New，找到你的python.exe

上手小测试：
----

首先配置你的APP_KEY和APP_SECRET：
在/src/snsapi/plugin/conf/config.json.example里面填写你的APP_KEY和SECRET。
将config.josn.example重命名为config.json。

然后执行程序：
cd SNSAPI_ROOT/src，
python test.py。
之后会弹出网页，填入账号密码后点授权，接着从跳转的页面的地址栏里复制出url，填入console(cmd)窗口中，
应该就能得到home_timeline了。good luck。另外：整个工程使用utf-8编码的，所以如果在windows的cmd窗口
中运行程序可能出现编码问题