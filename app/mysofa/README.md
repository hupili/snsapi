mysofa
====

**Warning: The code is under reconstruction using new SNSAPI interface. Do not use this app until it is done.**

Hope this be a super simple example to motivate you using snsapi~

Caveats
----

This App is a demo before our 2nd round of intensive restructure. 
The implementation is far from optimal now. One can simplify the 
script to around 20 lines using our latest SNSPocket class. 
Welcome anyone contribute.  -- HU Pili, 20121018

Introduction
----

mysofa reads statuses of Renren,
watch for certain conditions,
and then replies them. 
You can use it to grab sofa everytime!
This is how it gets the name.

By a few modifications, you can reply your 
girlfriend whenever she posts a new status. 
No matter it is rainy, sunny or stormy;
No matter it is course time, midnight, or coding time;
etc. 
You'll never miss one piece!
Imagine how astonished she is!
Of course, you can add some random delay 
to make this look as natural as possible. 
You also do not want to reply a smile image every time. 
Work out some intelligent stuffs~
(there are some pointers in the end of this document)
You are geeks! 
You can do it!
I believe you!

First Test
----

   * Go to [http://app.renren.com/developers/newapp](http://app.renren.com/developers/newapp)
   and apply for a new application.
   Believe me, it does not take you more than 
   2 minutes. Visualizing your girlfriend's face. 
   It's absolutely worth the time!
   * For Linux user, run './deploy.sh'. 
   Equivalently you can manually make links
   of '../../snsapi' and '../../conf' to 
   the current folder. Here's how the directory tree
   looks then

<img src="https://raw.github.com/hupili/snsapi/master/src/app/mysofa/pics/renren_sofa_1.jpg" />

   * Copy 'conf/channel.json.example' to 
   'conf/channel.json' and configure your 
   Renren channel accordingly. 
   If you have hard time understanding the 
   config file, use the following sample:

```
[
{
  "channel_name": "renren_account_1", 
  "open": "yes", 
  "platform": "renren", 
  "app_key": "", 
  "app_secret": "",
  "user_id": "",
  "auth_info":
  {
    "callback_url": "http://graph.renren.com/oauth/login_success.html",
    "cmd_fetch_code": "(built-in)",
    "cmd_request_url": "(built-in)",
    "save_token_file": "(built-in)"
  }
}
]
```

   You have to fill in your own "app_key" and 
   "app_secret". You get them in the first step.
   * Run 'python mysofa.py' .
   It runs like this. 

<img src="https://raw.github.com/hupili/snsapi/master/src/app/mysofa/pics/renren_sofa_2.jpg" />

A Step Further
----

You may noticed that mysofa managed to read one status
but nothing happened after that. 
OK, it means everything is working well. 
It's time to look into the simple codes. 
Here are some pointers:
   * 'MYSOFAR_NEWS_QUERY_COUNT' :
   How many statuses are read in one execution. 
   * 'MYSOFAR_REPLY_GAP' :
   How long do you wait between two replies. 
   It is suggested to be 10 seconds. 
   Or the server may reply 
   "service unavailable". 
   * 'MYSOFAR_REPLY_STRING' :
   What do you reply every time. 
   * 'can_reply()' : 
   The filtering rules. 
   By default, it only replies the statuses 
   posted by the users how have "hpl" in 
   their names. I just don't want to bother 
   other people in the test stage. You can change
   it to your girl friend's name, or 
   more complex rules!

You can make a cron job to let the script 
running periodically. 
Renren's token expires in 30 days. 
After initial authentication, you can copy 
the whole thing to your server and do not
worry about re-authentication for a month. 
Or, you can modify 'mysofa.py' directly. 
Infinitely loop the the main() function 
with proper delay. 

Leap Forward
----

I know you won't stop here. 
Now let's do something intelligent. 
Supposingly, after a few trials and 
modifications of the codes, you already 
get a hint of how to use SNSAPI. 
Other channels DO have the same flavour. 
Here's how to leverage the Internet to work for you:
   * Find some weather report rss. 
   e.g. [http://www.weather.com/weather/rss/subscription/](http://www.weather.com/weather/rss/subscription/)
   * Configure two channels, one for the weather
   feeds and the other for Renren. 
   * Find the information you need from the weather rss. 
   * Reply by something like:
   "It's so hot. Drink more water. :)" ;
   "It's very cold. Dress more."; 
   etc. 
   * You can also give some hearty reminder 
   according to the current system time:
   "Don't stay up too late in the night, baby. 
   It's already 11:50pm". 
   * You can also do some NLP analysis of 
   the thing she posts and reply accordingly!

Closing Remarks
----
I don't have enough time to build all these ideas. 
There are many upgrades of 'snsapi' waiting for me. 
I tried hard to come up with this simple document, 
attracting your interest, helping you jumpstart, 
and motivating your wildest dreams.  
We did a lot (and is continue doing) 
for the underlying layers. 
Hope you can focus on the upper layer logic. 
Come on, make some crazy applications!

   * We look forward to any people who 
can write new plugins to enable more channels. 
   * We look forward to any people who 
can help to maintain the project. 
   * We look forward to any people who 
are willing to make the architecture more clear. 
