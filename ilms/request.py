import requests
from functools import partialmethod


class RequestProxyer:

    def __init__(self, session):
        self.session = session

    def request(*args, **kwagrs):
        return requests.get(*args, **kwagrs)

    def request_auth(self, *args, **kwagrs):
        return self.session.get(*args, **kwagrs)

    get = partialmethod(request_auth)
