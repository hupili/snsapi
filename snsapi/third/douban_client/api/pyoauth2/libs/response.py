# -*- coding: utf-8 -*-
from .utils import urlparse


def to_query(txt):
    qs = urlparse.parse_qsl(txt)
    ret = dict(qs)
    return _check_expires_in(ret)


def to_text(txt):
    return txt


def _check_expires_in(ret):
    expires_in = ret.get('expires_in')
    if expires_in and expires_in.isdigit():
        ret['expires_in'] = int(expires_in)
    return ret


class Response(object):

    def __init__(self, response, **opts):
        self.resp = response
        self.status_code = self.status = response.status_code
        self.reason = response.reason
        self.content_type = response.headers.get('content-type')
        self.body = response.text

        options = {'parse': 'text'}
        options.update(opts)
        self.options = options

    def __repr__(self):
        return '<OAuth2 Response>'

    @property
    def parsed(self):
        fmt = self.options['parse']
        if fmt == 'json':
            return self.resp.json()
        elif fmt == 'query':
            return to_query(self.body)
        else:
            return self.body
