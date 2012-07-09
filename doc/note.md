Development notes
====

This file is used to record the development 
milestones, trace features, store meeting 
minutes and put down developers comments as a memo. 

20120706.hupili
----

TODO list:
   * An example to help users jumpstart
   * Read configurations from file, instead of writting in '.py' file. 
   (avoid commiting in those secrets by mistake...
   used to happen in another project...)
   * Upgrade '.gitignore' file to avoid commiting in 
   non-source files. (e.g. '.pyc')

20120709.hupili
----
(brainstorm)

Thoughts after 1st successful test:
   * Abstraction of channels, provided by plugin script files. 
   * Realization of channles, provided by configuration files. 

A channel is a certain method / place to get / put information. 
App layer developers / users can decide which channel he wants to use
through configurations. 
Currently, the abstraction and realization are 
binded through 'platform' string. 
It could be better that we write logic in script files
to provide the abstract description of a channel
and leave the realization to configurations. 
One example benefit is: a user can have multiple 
accounts on Sina Weibo; in the new design, he will not 
be constrained to one account. 

We construct a user story based on this flexibility:
   * He watches three blogs regularly. 
   * He has two Sina Weibo accounts. 
   * On one account, he follow IT news and share 
   	 them with his friends. 
   * On the other account, he follow gossips
   	 and share them with his friends. 
   * The three blogs update high quality content frequently. 
   * He forward those blog posts to his two accounts
   	 according to their category. (maybe using 'long weibo' tool). 

We leave analysis and filtering logic to threads. 
The basic building blocks provided by 'snsapi' is 
a multiple-read-multiple-write function. 
A sample configuration(realization of channels)
file may look like:
```
  {
    "channel_name": "sina_account1", 
    "platform": "sina", 
    "app_key": "", 
    "app_secret": "",
    "user_name": "sample_name1",
  }
  {
    "channel_name": "sina_account2", 
    "platform": "sina", 
    "app_key": "", 
    "app_secret": "",
    "user_name": "sample_name2",
  }
  {
    "channel_name": "blog_feed_1", 
    "platform": "rss", 
    "url": "sample_url1",
  }
  {
    "channel_name": "blog_feed_1", 
    "platform": "rss", 
    "url": "sample_url2",
  }
  {
    "channel_name": "blog_feed_1", 
    "platform": "rss", 
    "url": "sample_url2",
  }
```
   * "channel_name" is the identifier of a channel. 
   * "platform" gives the abstraction name of a channel. 
   The notion is very like "class" name in OOP. 
   So a channel can be understood as "instance". 
   * Other fields are "platform"-specific. 

Not all channels support the full set of functions. 
It is the application layer's resposibility to enumerate 
supported methods(login/read/write) and then decide 
whether and how to use this channel. 
