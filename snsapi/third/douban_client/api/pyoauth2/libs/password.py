# -*- coding: utf-8 -*-

from .base import Base


class Password(Base):

    def authorize_url(self):
        return NotImplementedError('The authorization endpoint is not used in this strategy')

    def get_token(self, username, password, **opts):
        params = {'grant_type': 'password',
                  'username': username,
                  'password': password,
                  }
        params.update(self.client_params)
        opts.update(params)
        return self.client.get_token(**opts)
