# -*- coding: utf-8 -*-
from .base import Base


class AuthCode(Base):

    def __repr__(self):
        return '<OAuth2 AuthCode %s>' % self.client.id

    def authorize_params(self, **params):
        params.update({'response_type': 'code', 'client_id': self.client.id})
        return params

    def authorize_url(self, **params):
        params = self.authorize_params(**params)
        return self.client.authorize_url(params)

    def get_token(self, code, **opts):
        params = {'grant_type': 'authorization_code', 'code': code}
        params.update(self.client_params)
        opts.update(params)
        return self.client.get_token(**opts)
