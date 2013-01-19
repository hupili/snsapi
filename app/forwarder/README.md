forwarder 
====

This is a general purpose forwarder. 
You can configure some in-channels and some out-channels. 
In-channels should support the function `home\_timeline()`
and out-channels should support the function `update()`.
The forwarder only supports staight forwarding at present. 
Since too fast forwarding will cause failure, 
we restrict it to 1 forward / 1 channel / 1 run. 
You can set the "quota" in `forwarder.py`, 
or add sleep period. 

Deployment and Initial Test
----

By default, the following operations assume 
you're under the same folder as the current file. 

   * Configure `channel.json` and `forwarder.json` accordingly. 
   You can try `snscli` first for a self-contianed tutorial of 
   configuration `channel.json`. 
   `forwarder.json` only contains two JSON-lists: 
   `channel_in` and `channel_out`. 
   Please follow the examples in the file. 
   * Manually run the forwarder:
```
python forwarder.py
```

Advanced
----

   * You can reset the 'messages.json', to erase the 
   memory of all messages. 
   The initial 'messages.json' is an empty map. 
```
{}
```

   * To limit number of messages queried in one invoke, 
   you can set the `count` entry in `channel.json`. 
   * To limit the number of messages write to one channel, 
   you can set `quota` dict in `forwarder.json`. 

Screenshots (OLD)
----

The following screenshots are from running the 
[old verion](old/)
forwarder. 
The current new one simply restructure the code to make it much much simpler. 
You can preview the effect from the screenshots. 

Configure Sina Weibo to be one in channel, 
and QQ Microblog to be one out channel. 
Invoke `python forwarder.py` and pass all the authorization. 
It forwards the first message:

![cli 1](https://raw.github.com/hupili/snsapi/master/app/forwarder/screenshots/old/forwarder3.jpg)

Now I publish some news on the Sina weibo through web interface:

![sina web](https://raw.github.com/hupili/snsapi/master/app/forwarder/screenshots/old/forwarder1.jpg)

Invoke forwarder again. 
forwarder remembers the messages it has forwarded and avoid repitition. 
It forwards the newly published status on Sina:

![cli 2](https://raw.github.com/hupili/snsapi/master/app/forwarder/screenshots/old/forwarder4.jpg)

This is what we see on QQ microblog:

![qq web](https://raw.github.com/hupili/snsapi/master/app/forwarder/screenshots/old/forwarder2.jpg)


Remarks
----

The forwarder app is by no means complete. 
It is just a demo of the basic idea. 
You can modify the codes a little 
and setup some rules governing the forwarding behaviour.
