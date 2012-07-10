Development notes
====

This file is used to record the development 
milestones, trace features, store meeting 
minutes and put down developers comments as a memo. 

20120710.lijunbo
----

Reply for 20120709.hupili

Good job!

User may have several accounts in one platform. The configuration file
for user is a good idea. but APP_KEY and APP_SECRET should not be seen by 
users, so I think APP_KEY should be placed in "plugin script file", being
part of the ultimate binary code when distributing. One platform be given 
one APP_KEY is enough. 

so I think the user configuration file will be like:
```
  {
    "channel_name": "sina_account1", 
    "platform": "sina", 
    "user_name": "sample_name1",
  }
```

I like the conception of channel. Different platforms just like different
local area networks, when we put channels between them, then information 
flows even wider. But information may attenuate when transfering from one 
platform to another. 
