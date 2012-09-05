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
    def __init__(self, fname="conf/channel.json"):
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

class NoSuchChannel(ConfigError):
    def __str__(self):
        return "No Such Channel. Please check your 'channel.json'. Or do you forget to set snsapi.channel_name before calling read_config()?"

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

class SNSEncodingError(SNSError):
    def __init__(self):
        super(SNSEncodingError, self).__init__()
    def __str__(self):
        return "Do not evaluate our interface objects using str(). " \
                "Internal data structure of the entire project is " \
                "unicode. For text exchange with other parties, we " \
                "stick to utf-8"

class snsAuthFail(SNSError):
    def __str__(self):
        return "Authentication Failed!"

class snsWriteFail(SNSError):
    def __str__(self):
        return "This channel is non-writable"
    
class RenRenAPIError(SNSError):
    def __init__(self, code, message):
        Exception.__init__(self, message)
        self.code = code

class SNSPocketDuplicateName(SNSError):
    def __init__(self):
        super(SNSPocketError, self).__init__()
    def __str__(self):
        return "Encounter a duplicate channel name!"

class SNSPocketError(SNSError):
    def __init__(self):
        super(SNSPocketError, self).__init__()
    def __str__(self):
        return "SNSPocket Error!"

class SNSPocketSaveConfigError(SNSPocketError):
    def __init__(self):
        super(SNSPocketSaveConfigError, self).__init__()
    def __str__(self):
        return "SNSPocket Save Config Error!"
        
