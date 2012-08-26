auxiliary 
====

This folder contains auxiliary scritps. 
In principle, they are not a necesary part of 'snsapi'. 
Some of them are useful to make your deployment individulized. 
Without those scripts, your 'snsapi' should still 
work well by default. 

File list
----

   * 'request_url_wget.sh'. Request url through 'wget', instead of default webbrowser.
   * 'fetch_code_local.sh'. Pull authenticated code from local storage. 
     By default, this script is invoked after 'request_url_wget.sh'. 
   * 'auto.sh'. A general purpose auto executing script. 
     It is assumed to be invoked by cron. 
     This script help you enable and disable some auto command 
     in an easier way. 
