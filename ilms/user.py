import requests

from ilms.route import route


class LoginError(Exception):
    pass


class User:

    def __init__(self, uid, pwd):
        self.uid = uid
        self.pwd = pwd
        self.session = requests.Session()
        self.email = None

    def login(self):
        resp = self.session.post(
                route.login_submit,
                data={'account': self.uid, 'password': self.pwd})
        json = resp.json()
        if json['ret']['status'] == 'false':
            raise LoginError
        self.email = json['ret']['email']
        return json
