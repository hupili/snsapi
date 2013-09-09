# Renren Backup Demo App

You can easily extend the 10 lines app to any other platforms supported by SNSAPI.
As a demo, it does not take message deduplication into consideration. 
You can see `forwarder.py` and `mysofa.py` for example deduplication methods.

## Usage

   * Copy `conf/channel.json.example` to `conf/channel.json`. 
   Fill in your credentials accordingly, 
   e.g. `app_key` and `app_secret`.
   * Configure on Renren dev platform. 
   Make sure the domain name there matches the `callback_url` in `conf/channel.json`.
   * Run the script `python backup.py`.
   * Your browser will be prompt to Renren's OAuth page.
   * After authorize on Renren, 
   we'll get the code and accomplish following procedures automatically.

## More

Recommend you use all default configurations as an initial test. 
You can change the `callback_url` to your own later but make sure
the `code` returned by OSN is redirected to SNSAPI.
See [SNSAPI Configuraiton](https://github.com/hupili/snsapi/wiki/Configurations)
for more information.
