forwarder
====

This is a general purpose forwarder. 
You can configure some in channels and some out channels. 
In channels should support the function 'home\_timeline()'
and out channels should support the function 'update()'
The forwarder only supports staight forwarding at present. 
Since too fast forwarding will cause failure, 
we restrict it to 1 forward / 1 channel / 1 run. 
You can set the 'quota' in 'forwarder.py', 
or add sleep period. 


Deployment and Initial Test
----

By default, the following operations assume 
you're under the same folder as the current file. 

   * Make symbolic links to essential 'snsapi' components: 
```
ln -s ../../snsapi
ln -s ../../auxiliary
```
   * Copy default configurations:
```
cp channel.json.example channel.json
cp forwarder.json.example forwarder.json
```
   * By default, two RSS channels are configured
   as in channels, which points 
   to the test RSS files in the repo. 
   1 Sina channel is configured as out channels. 
   * Fill in your 'app_key' and 'app_secret'
   in 'channel.json'. 
   * Manually run the forwarder:
```
python forwarder.py
```

If the intial test is OK, you can try to configure your own 
channels and forwarding policies. 

Configurations
----

All configurations are written in json style. 

'channel.json':
   * This is universal to all snsapi. 
   Please refer to the document of 'snsapi'. 

'forwarder.json':
   * 'channel_in': a list of all in channels. 
   * 'channel_out' a list of all out channels. 

Advanced
----

   * You can reset the 'messages.json', to erase the 
   memory of all messages. 
   The initial 'messages.json' is an empty map. 
```
{}
```

Screenshots
----

Configure Sina Weibo to be one in channel, 
and QQ Microblog to be one out channel. 
Invoke `python forwarder.py` and pass all the authorization. 
It forwards the first message:

![cli 1](https://raw.github.com/uxian/snsapi/master/app/forwarder/screenshots/forwarder3.jpg)

Now I publish some news on the Sina weibo through web interface:

![sina web](https://raw.github.com/uxian/snsapi/master/app/forwarder/screenshots/forwarder1.jpg)

Invoke forwarder again. 
forwarder remembers the messages it has forwarded and avoid repitition. 
It forwards the newly published status on Sina:

![cli 2](https://raw.github.com/uxian/snsapi/master/app/forwarder/screenshots/forwarder4.jpg)

This is what we see on QQ microblog:

![qq web](https://raw.github.com/uxian/snsapi/master/app/forwarder/screenshots/forwarder2.jpg)
