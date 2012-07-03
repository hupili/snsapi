#!/usr/bin/env python
# -*- coding: utf-8 -*-

import oauth
import webbrowser

app_key = ''
app_secret = ''

if __name__ == "__main__":
    callback_url = "http://copy.the.code.to.client/"
    cli = oauth.APIClient(app_key, app_secret, callback_url)
    url = cli.get_authorize_url()
    webbrowser.open(url)
    
    code = raw_input()
    token = cli.request_access_token(code)
    print token
    cli.set_access_token(token, -1)