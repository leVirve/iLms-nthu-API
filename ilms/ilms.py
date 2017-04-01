import os

from ilms import parser
from ilms.route import route
from ilms.request import RequestProxyer
from ilms.utils import ProgressBar

reqs = RequestProxyer()


class LoginError(Exception):
    pass


class User:

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.email = None

    def login(self):
        resp = reqs.post(
                route.login_submit,
                data={'account': self.user, 'password': self.pwd})
        json = resp.json()
        if json['ret']['status'] == 'false':
            raise LoginError
        self.email = json['ret']['email']
        return json


class Item():

    def download(self):
        for target in self.details:
            download(target['id'])


class Homework(Item):

    def __init__(self, raw, callee):
        self.raw = raw
        self.callee = callee
        self.uid = raw['id']

    def detail(self):
        resp = reqs.get(
            route.course(self.callee.course_id).homework(self.uid))
        self.details = parser.parse_homework_detail(resp.text).result
        return self.details


class Material(Item):

    def __init__(self, raw, callee):
        self.raw = raw
        self.callee = callee
        self.uid = raw['id']

    def detail(self):
        resp = reqs.get(
            route.course(self.callee.course_id).document(self.uid))
        self.details = parser.parse_material_detail(resp.text).result
        return self.details


class Course():

    def __init__(self, raw, callee):
        self.raw = raw
        self.callee = callee
        self.course_id = raw['id']

    def get_homeworks(self):
        resp = reqs.get(route.course(self.course_id).homework())
        self.homeworks = [
            Homework(homework, callee=self)
            for homework in parser.parse_homework_list(resp.text).result
        ]
        return self.homeworks

    def get_materials(self, download=False):
        resp = reqs.get(route.course(self.course_id).document())
        self.materials = [
            Material(material, callee=self)
            for material in parser.parse_material_list(resp.text).result
        ]
        return self.materials

    def get_forum_list(self, page=1):
        resp = reqs.get(
            route.course(self.course_id).forum() + '&page=%d' % page)
        return parser.parse_forum_list(resp.text)


class System():

    def __init__(self, user):
        self.profile = None
        self.courses = None

    def get_profile(self):
        resp = reqs.get(route.profile)
        self.profile = parser.parse_profile(resp.text)
        return self.profile

    def get_courses(self):
        resp = reqs.get(route.home)
        self.courses = [
            Course(course, callee=self)
            for course in parser.parse_course_list(resp.text).result]
        return self.courses

    def get_post_detail(self, post_id):
        resp = reqs.post(route.post, data={'id': post_id})
        return parser.parse_post_detail(resp.json())


def download(attach_id, folder='download'):
    resp = reqs.get(route.attach.format(attach_id=attach_id), stream=True)

    filename = resp.headers['content-disposition'].split("'")[-1]
    filesize = int(resp.headers['content-length'])

    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    chunk_size = 1024
    progress = ProgressBar()
    progress.max = filesize // chunk_size
    with open(path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
            progress.next()
    progress.finish()
    return filename
