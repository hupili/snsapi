# Auth Aux Scripts

Those scripts were developed before have the HTTP server to fetch code.
Now you can safely ignore them in order to try SNSAPI out. 
However, if you want to extend the authorization behaviour, 
you can look at those scripts and how they are associated with 
the two stage of authorization. 

## How to use?

You can try to configure corresponding entry in `channel.json` to the following. 

```
"auth_info":
{
  "callback_url": "http://copy.the.code.to.client/",
  "cmd_fetch_code": "./auxiliary/auth/fetch_code_local.sh",
  "cmd_request_url": "./auxiliary/auth/request_url_wget.sh",
  "save_token_file": "(default)"
}
```

If you login the OSN (say SinaWeibo), export cookie to current dir and run `snscli`, 
it will automatically authorize using this auxiliary scripts. 
The advantage is that not until your cookie is expired, 
it can always authorize without user intervention. 

## TODO

This two scripts are not frequently used. 
Please verify whether they work before real deployment. 
Feel free to upgrade them if you find problems. 
