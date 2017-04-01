import requests
from functools import partialmethod


def encode_utf8(func):
    def f(*args, **kwargs):
        r = func(*args, **kwargs)
        r.encoding = 'utf8'
        return r
    return f


class RequestProxyer:

    def __init__(self, session=None):
        self.session = requests.Session()

    @encode_utf8
    def request(*args, **kwagrs):
        return requests.get(*args, **kwagrs)

    @encode_utf8
    def request_auth(self, method, *args, **kwagrs):
        return self.session.request(method, *args, **kwagrs)

    get = partialmethod(request_auth, 'GET')
    post = partialmethod(request_auth, 'POST')
