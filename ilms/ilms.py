import ilms
from ilms.request import RequestProxyer
from ilms.parser import *


class iLms:

    def __init__(self, session):
        self.session = session
        self.requests = RequestProxyer(self.session)

    def get_course_list(self):
        resp = self.requests.get(ilms.config.home)
        resp.encoding = 'utf8'
        return parse_course_list(resp.text)
