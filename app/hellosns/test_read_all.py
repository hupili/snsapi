# -*- coding: utf-8 -*-
'''
Read timeline from all configured channels

docstring placeholder
'''

from snsapi.snspocket import SNSPocket
from snsapi.utils import console_input,console_output

if __name__ == "__main__":
    sp = SNSPocket()
    sp.load_config()

    sp.auth()

    sl = sp.home_timeline()

    print sl
