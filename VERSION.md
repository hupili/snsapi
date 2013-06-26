SNSAPI 0.4.3
============

Version string convention: `x.y.z`

   * `x`: Major version with architectural upgrades. 
   * `y`: Minor version with functional extension. 
   * `z`: Micro version with small fix. 

0.4.4
-----

   * Unify the Sina API request to `weibo_request()` method. 
   * SinaWeibo support specialized forwarding. 
   * Code clean for `snsgui.py`. 

0.4.3
-----

   * URL expanding service (recursive) in SNSBase.
   * URL shortening service for SinaWeibo.
   * docstring upgrade for some platforms. 
   * A word translation demo. 
   * snsgui, GUI of SNSAPI built on Tkinter.

0.4.2
-----

   * Two new methods for auto authorization prototyped for SinaWeiboStatus:
   1) Use remote Autoproxy (see https://github.com/xuanqinanhai/weibo-simulator );
   2) Use local username/password. 
   * Upgrades for Sphinx autodoc:
   1) improve decorator `require_authed` to retain docstring; 
   2) make apps autodoc-able;
   3) docstring upgrade to conform to Sphinx style;
   * More UTs for snsbase methods: `_parse_code`; expiration check. 

0.4.1
-----

   * Fix `load_config` in `app/hellosns/`
   * Email platform: check expire;
   support decode email header; 
   support parse 'reply-to' header field;
   * Fix import path error of unit test.
   * More sample unit test of email channel. 
   * Fix unicode error of `app/clock/`
   * Fix Sphinx document. 
   * All defaut auth helper is changed to http://snsapi.sinaapp.com/auth.php
   * Support Module test of `renren.py` and `sina.py`. 


0.4
----

   * New auth flow functions: `is_authed`, `need_auth`, `is_expired`. 
   * Use `requirement.txt` to maintain dependency. 
   * Add a "clock" demo app. 
   * Rewrite "forwarder" using new architecture. 
   * Support limiting home_timeline's count by config. (handy to operate multiple channels). 
   * JsonDict function support stronger `get`: enumerate a list of properties. (handy to parse different version of data source)
   * Fix an RSS date parsing error. 
   * Change to nosetests. 

0.3
---

   * Restructure nested Message class, allowing them to be pickled. 
   * Fault tolerant auth flow. 
   * Fault tolerant HTTP request/response. 
   * A `report_time` decorator is added to `utils`. 
   You can use it to get execution time of functions. 
   * A `require_authed` decorator is added to `snsbase`. 
   Plugin developers should put it before the methods, 
   whose invokation require a authed state. 
   * Fix Tencent Weibo html entity problem. 
   The texts in Message object is unified to have html entities unescaped. 

0.2
---

   * New platform reference mechanism. 
   Support trial platforms. 
   * One module file -> multiple platforms. 
   This allows better code reuse. 
   * Message class is re-designed. 
   * Three levels of Message dump methods for different application. 
   * Add SQLite platform. 
   * Add Email platform. 
   * Add Twitter platform. 

0.1
---

   * Initial framework. 
   * Setup website. 
