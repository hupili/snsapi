# -*- coding: utf-8 -*-
#
# Convert Google Reader subscription.xml to SNSAPI's channel.json
# You can download your subscription data from Google Takeout:
#
#    * https://www.google.com/takeout
# 

from lxml import etree
import json

def gr2snsapi(gr_str):
    root = etree.XML(gr_str)
    ret = []
    num = 0
    for e in root.iter('outline'):
        num += 1
        if e.get('type', None):
            ret.append({
                'platform': 'RSS',
                'open': 'yes', 
                'url': e.get('xmlUrl'),
                'channel_name': 'ch%d. %s' % (num, e.get('title')), 
                '__other__info': { 
                    'html_url': e.get('htmlUrl'),
                    'text': e.get('text')
                    }
                })
    return json.dumps(ret, indent=2)

def main(i, o):
    f_in = open(i, 'r') if isinstance(i, str) else i
    f_out = open(o, 'w') if isinstance(o, str) else o
    f_out.write(gr2snsapi(f_in.read()))
    f_in.close()
    f_out.close()

if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Convert Google Reader subscription.xml to SNSAPI's channel.json")
    parser.add_argument('-i', metavar='INPUT', type=str, 
            help='filename of input (e.g. subscription.xml)',
            default=sys.stdin)
    parser.add_argument('-o', metavar='OUTPUT', type=str, 
            help='filename of output (e.g. channel.json)',
            default=sys.stdout)
    args = parser.parse_args()

    main(**vars(args))
