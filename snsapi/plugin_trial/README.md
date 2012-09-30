# Trial Plugins

Trial plugins goes into this directory. 
After full testing and code quality auditing, 
it will be moved to "plugin" directory. 

We allow kludgery plugins in this directory. 
e.g. copy a full functioning encapsulation of certian 
platform into this directory and only do method
routing to fit into SNSAPI framework. 
Before moving to formal "plugin" directory, 
it must be tailored to keep the code tidy and clean. 

Basic requirements to bring a trial plugin to formal plugin:

   * Only keep essential functionality. 
   * Reuse common operations provided in lower layer. 
   e.g. `_http_get` in SNSAPI. 

To disable/enable trial plugins please see "../platform.py". 
