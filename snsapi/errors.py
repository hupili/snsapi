#-*- encoding: utf-8 -*-

'''
Errors or Exceptions for SNSAPI

How to add an error type?

   * Check out ``Mark1`` (in ``errors.py``).
     Inherit your error type from a right class.
     The ``#>>`` comment denotes the level an error type is in.
   * Check out ``Makr2`` (in ``errors.py``).
     Add your new error type to the corresponding tree.

How to reference an error type?

   * By convention, others should only import "snserror".
     e.g. ``from errors import snserror``, or
     ``from snsapi import snserror``.
   * Use dot expression to enter the exact type.
     e.g. ``snserror.config.nofile``.

'''


# =============== Error Type ==============

# Mark1

#>
class SNSError(Exception):
    def __str__(self):
        return "SNSError!"

#>>
class ConfigError(SNSError):
    def __str__(self):
        return "SNS configuration error!"

#>>>
class NoConfigFile(ConfigError):
    def __init__(self, fname="conf/channel.json"):
        self.fname = fname
    def __str__(self):
        return self.fname + " NOT EXISTS!"

#>>>
class NoPlatformInfo(ConfigError):
    def __str__(self):
        return "No platform info found in snsapi/plugin/conf/config.json. \
        self.platform and platform in snsapi/plugin/conf/config.json must match."

#>>>
class MissAPPInfo(ConfigError):
    def __str__(self):
        return "Please config the file snsapi/plugin/conf/config.json. \
        You may forget to add your app_key and app_secret into it"

#>>>
class NoSuchPlatform(ConfigError):
    def __str__(self):
        return "No Such Platform. Please check your 'channel.json'."

#>>>
class NoSuchChannel(ConfigError):
    def __str__(self):
        return "No Such Channel. Please check your 'channel.json'. Or do you forget to set snsapi.channel_name before calling read_config()?"

#>>
class SNSTypeWrongInput(SNSError):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return "Wrong input for snsType initializing! It must be a dict\n"+str(self.value)

#>>
class SNSTypeError(SNSError):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return "errors when when dealing snsType." + self.value

#>>>
class SNSTypeParseError(SNSError):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return "errors when parsing JsonObject for snsType: " + self.value

#>>
class SNSEncodingError(SNSError):
    def __init__(self):
        super(SNSEncodingError, self).__init__()
    def __str__(self):
        return "Do not evaluate our interface objects using str(). " \
                "Internal data structure of the entire project is " \
                "unicode. For text exchange with other parties, we " \
                "stick to utf-8"

#>>
class SNSAuthFail(SNSError):
    def __str__(self):
        return "Authentication Failed!"

#>>>
class SNSAuthFechCodeError(SNSAuthFail):
    def __str__(self):
        return "Fetch Code Error!"

#>>
class SNSOperation(SNSError):
    def __str__(self):
        return "SNS Operation Failed"

#>>>
class SNSWriteFail(SNSOperation):
    def __init__(self, value):
        super(SNSWriteFail, self).__init__()
        self.value = value
    def __str__(self):
        return "This channel is non-writable: %s" % self.value

#>>>
class SNSReadFail(SNSOperation):
    def __str__(self):
        return "This channel is non-readable"

#>>
class SNSPocketError(SNSError):
    def __init__(self):
        super(SNSPocketError, self).__init__()
    def __str__(self):
        return "SNSPocket Error!"

#>>>
class SNSPocketSaveConfigError(SNSPocketError):
    def __init__(self):
        super(SNSPocketSaveConfigError, self).__init__()
    def __str__(self):
        return "SNSPocket Save Config Error!"

#>>>
class SNSPocketLoadConfigError(SNSPocketError):
    def __init__(self, msg = ""):
        super(SNSPocketLoadConfigError, self).__init__()
        self.msg = msg
    def __str__(self):
        return "SNSPocket Load Config Error! %s" % self.msg

#>>
class SNSPocketDuplicateName(SNSError):
    def __init__(self, cname):
        super(SNSPocketDuplicateName, self).__init__()
        self.channel_name = cname
    def __str__(self):
        return "Encounter a duplicate channel name!"

# ========= Error Tree ==================

# Mark2

class snserror(object):
    config = ConfigError
    config.nofile = NoConfigFile
    config.save = SNSPocketSaveConfigError
    config.load = SNSPocketLoadConfigError

    type = SNSTypeError
    type.parse = SNSTypeParseError

    op = SNSOperation
    op.read = SNSReadFail
    op.write = SNSWriteFail

    auth = SNSAuthFail
    auth.fetchcode = SNSAuthFechCodeError
