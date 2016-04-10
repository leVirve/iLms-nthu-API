import ilms
from ilms.request import RequestProxyer
from ilms.parser import *


class iLms:

    def __init__(self, session):
        self.session = session
        self.requests = RequestProxyer(self.session)

    def get_course_list(self):
        resp = self.requests.get(ilms.config.home)
        return parse_course_list(resp.text)

    def get_homework_list(self, course_id):
        resp = self.requests.get(ilms.config.hwlist % course_id)
        return parse_homework_list(resp.text)

    def get_homework_detail(self, course_id, homwework_id, download=False):
        resp = self.requests.get(ilms.config.hwdetail
                                 % (course_id, homwework_id))
        if download:
            pass
        return parse_homework_detail(resp.text)

    def get_forum_list(self, course_id, page=1):
        resp = self.requests.get(ilms.config.forum % (course_id, page))
        return parse_forum_list(resp.text)

    def get_post_detail(self, post_id):
        resp = self.requests.post(ilms.config.post, data={'id': post_id})
        return parse_post_detail(resp.json())

    def get_doc_list(self, course_id, download=False):
        resp = self.requests.get(ilms.config.doclist % course_id)
        return parse_doc_list(resp.text)

    def get_doc_detail(self, course_id, material_id):
        resp = self.requests.get(ilms.config.docdetail
                                 % (course_id, material_id))
        return parse_doc_detail(resp.text)
