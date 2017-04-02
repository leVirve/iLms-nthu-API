from functools import partialmethod

import requests

from ilms import utils


def encode_utf8(func):
    def f(*args, **kwargs):
        r = func(*args, **kwargs)
        r.encoding = 'utf8'
        return r
    return f


class RequestProxyer:

    def __init__(self, session=None):
        sess = utils.load_session()
        self.session = sess or session or requests.Session()

    def save_session(self):
        utils.save_session(self.session)

    @encode_utf8
    def request(*args, **kwagrs):
        return requests.get(*args, **kwagrs)

    @encode_utf8
    def request_auth(self, method, *args, **kwagrs):
        return self.session.request(method, *args, **kwagrs)

    get = partialmethod(request_auth, 'GET')
    post = partialmethod(request_auth, 'POST')
