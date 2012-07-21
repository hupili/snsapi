#-*- encoding: utf-8 -*-

'''
Errors or Exceptions for SNSAPI
'''

class SNSError(Exception):
    def __str__(self):
        return "SNSError!"
    
class ConfigError(SNSError):
    def __str__(self):
        return "SNS configuration error!"
    
class NoConfigFile(ConfigError):
    def __init__(self, fname="conf/config.json"):
        self.fname = fname
    def __str__(self):
        return self.fname + " NOT EXISTS!"
    
class NoPlatformInfo(ConfigError):
    def __str__(self):
        return "No platform info found in snsapi/plugin/conf/config.json. \
        self.platform and platform in snsapi/plugin/conf/config.json must match."
            
class MissAPPInfo(ConfigError):
    def __str__(self):
        return "Please config the file snsapi/plugin/conf/config.json. \
        You may forget to add your app_key and app_secret into it"    

class NoSuchPlatform(ConfigError):
    def __str__(self):
        return "No Such Platform. Please check your 'channel.json'."

class snsTypeWrongInput(SNSError):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return "Wrong input for snsType initializing! It must be a dict\n"+str(self.value)
    
class snsTypeParseError(SNSError):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return "errors when parsing JsonObject for snsType " + self.value

class snsAuthFail(SNSError):
    def __str__(self):
        return "Authentication Failed!"


