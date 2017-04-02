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

    def __init__(self, raw, callee):
        self.raw = raw
        self.callee = callee
        self.uid = raw['id']
        self.insert_attrs(raw)

    def insert_attrs(self, attrs):
        for key, val in attrs.items():
            setattr(self, key, val)

    def download(self):
        for target in self.detail:
            download(target['id'])


class Handin(Item):

    @property
    def detail(self):
        if hasattr(self, '_detail'):
            return self._detail
        resp = reqs.get(
            route.course(self.callee.callee.id).document(self.uid))
        self._detail = parser.parse_homework_handin_detail(resp.text).result
        return self._detail

    def __str__(self):
        return '<Homework Handin: %s>' % (self.authour)


class Homework(Item):

    @property
    def detail(self):
        if hasattr(self, '_detail'):
            return self._detail
        resp = reqs.get(
            route.course(self.callee.id).homework(self.uid))
        self._detail = parser.parse_homework_detail(resp.text).result
        return self._detail

    @property
    def handin_list(self):
        if hasattr(self, '_handin_list'):
            return self._handin_list
        resp = reqs.get(
            route.course(self.callee.id).homework_handin_list(self.uid))
        self._handin_list = [
            Handin(handin, callee=self)
            for handin in parser.parse_homework_handin_list(resp.text).result
        ]
        return self._handin_list

    def __str__(self):
        return '<Homework: %s>' % (self.title)


class Material(Item):

    @property
    def detail(self):
        if hasattr(self, '_detail'):
            return self._detail
        resp = reqs.get(
            route.course(self.callee.id).document(self.uid))
        self._detail = parser.parse_material_detail(resp.text).result
        return self._detail


class Course(Item):

    def get_homeworks(self):
        resp = reqs.get(route.course(self.uid).homework())
        self.homeworks = [
            Homework(homework, callee=self)
            for homework in parser.parse_homework_list(resp.text).result
        ]
        return self.homeworks

    def get_materials(self, download=False):
        resp = reqs.get(route.course(self.uid).document())
        self.materials = [
            Material(material, callee=self)
            for material in parser.parse_material_list(resp.text).result
        ]
        return self.materials

    def get_forum_list(self, page=1):
        resp = reqs.get(
            route.course(self.uid).forum() + '&page=%d' % page)
        return parser.parse_forum_list(resp.text)

    def __str__(self):
        return '<Course: %s %s>' % (self.course_id, self.name.get('zh'))


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
