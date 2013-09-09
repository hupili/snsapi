# -*- coding: utf-8 -*-

'''
snsapi Cryptography Tools
'''

import base64

class SNSCrypto(object):
    """snsapi cryptography tools"""
    def __init__(self):
        super(SNSCrypto, self).__init__()
        self.__init_crypt()

    def __init_crypt(self):
        """
        Init the crypto utility which will be called by
        __encrypt and __decrypt.

        """
        from third import pyDes
        self.crypt = pyDes.des("DESCRYPT", pyDes.CBC, "\0\0\0\0\0\0\0\0",\
                pad=None, padmode=pyDes.PAD_PKCS5)

    def __encrypt(self, string):
        """
        The delegate for encrypt utility.
        e.g. You can change the following use of pyDes
        to openssl if you have it. We use pyDes for by
        Default because we don't want o bother the user
        to install other softwares.

        See also, __init_crypt, __encrypt, __decrypt

        """
        return self.crypt.encrypt(string)

    def __decrypt(self, string):
        """
        The delegate for decrypt utility.

        See also, __init_crypt, __encrypt, __decrypt

        """
        return self.crypt.decrypt(string)


    def encrypt(self, string):
        """
        INPUT: any string
        OUTPUT: hexadecimal string of encrypt output

        The input string will first be encoded by BASE-64.
        This is to make sure the intermediate value is a
        printable string. It will be easier to change
        pyDes to other crypto utilities. After actual
        encryption delegated to other modules, the final
        output is also base64 encrypted, this makes it
        printable.

        """
        tmp1 = base64.encodestring(string)
        tmp2 = self.__encrypt(tmp1)
        tmp3 = base64.encodestring(tmp2)
        return tmp3

    def decrypt(self, string):
        """
        INPUT: hexadecimal string of encrypt output
        OUTPUT: any string

        Reverse process of decrypt

        """
        tmp1 = base64.decodestring(string)
        tmp2 = self.__decrypt(tmp1)
        tmp3 = base64.decodestring(tmp2)
        return tmp3

if __name__ == '__main__':
    c = SNSCrypto()
    plain = "Test Crypto wapper for SNSAPI!"
    secret = c.encrypt(plain)
    decplain = c.decrypt(secret)
    print "plain:%s\nsecret:%s\ndecrypted plain:%s\n" \
            % (plain, secret, decplain)
