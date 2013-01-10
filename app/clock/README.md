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
之后调用的自动读取（可配置不保存）。

## 配置文件


