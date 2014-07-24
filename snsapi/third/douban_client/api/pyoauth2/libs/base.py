# -*- coding: utf-8 -*


class Base(object):

    def __init__(self, client):
        self.client = client

    @property
    def client_params(self):
        return {'client_id': self.client.id, 'client_secret': self.client.secret}
