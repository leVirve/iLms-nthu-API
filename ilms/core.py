import os
import re

import requests

from ilms import parser
from ilms import exception
from ilms.route import route
from ilms.utils import (
    unzip_all, check_is_download, stream_download,
    json_dump, json_load, safe_str)

session = requests.Session()


class User:
    '''
    profile: dict() of login return status, containing 'email', 'name',
             'phone', 'info', 'divName', 'divCode'
    '''

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.session = session
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3379.0 Safari/537.36',
            'Refer': route.home,
        }
        self.profile = None

    def login(self):
        r = self.session.post(
                route.login_submit,
                data={'account': self.user, 'password': self.pwd}
            )
        r = r.json()['ret']

        status = r.pop('status')
        if status == 'false':
            raise exception.LoginError(r['msg'])

        self.profile = r
        return True


class Item():

    def __init__(self, raw, addtional):
        self.raw = raw
        self.uid = raw['id']
        self.insert_attrs(raw)
        self.insert_attrs(addtional)

    def insert_attrs(self, attrs):
        for key, val in attrs.items():
            setattr(self, key, val)

    def download(self):
        for target in self.detail:
            download(target['id'])


class ItemContainer():

    def __init__(self, elements, base_item, addtional={}):
        self.items = [base_item(e, addtional) for e in elements]

    def __getitem__(self, x):
        return self.items[x]

    def __iter__(self):
        return self.items.__iter__()

    def get(self, x):
        return self.items[x]

    def find(self, **query_kws):
        for item in self.items:
            for query_k, query_v in query_kws.items():
                if not query_v:
                    break
                targ = getattr(item, query_k)
                # if targ and isinstance(targ, str) and query_v not in targ:
                #     break
                if targ and isinstance(targ, str) and query_v in targ:
                    return item
                if targ and isinstance(targ, dict):
                    for targ_k, targ_v in targ.items():
                        if query_v in targ_v:
                            return item
                    else:
                        break
            else:
                return item


class Handin(Item):

    @property
    def detail(self):
        if not hasattr(self, '_detail'):
            r = session.get(route.course(self.course_id).document(self.uid))
            self._detail = parser.parse_homework_handin_detail(r)
        return self._detail

    def download(self, root_folder):
        folder_name = os.path.join(root_folder, '%s-%s' % (self.account_id, self.authour))
        if check_is_download(folder_name, ['*.zip', '*.rar']):
            return
        for target in self.detail:
            download(target['id'], folder=folder_name)
        unzip_all(folder_name)

    def set_score(self, score):
        if self.is_group:
            r = session.get(route.query_group.format(
                course_id=self.course_id,
                folder_id=self.score['folder_id'],
                team_id=self.score['team_id']))
            # import pdb; pdb.set_trace()
            raise Exception('not implemented yet 2018/03/28')

        score_id = self.score.get('score_id')
        assert int(score_id)

        params = {'score': score, 'id': score_id}
        r = session.post(route.score, params=params)

        assert r.ok
        return r

    def __str__(self):
        return safe_str('<Homework Handin: %s-%s>' % (self.account_id, self.authour))


class Homework(Item):

    @property
    def detail(self):
        if not hasattr(self, '_detail'):
            r = session.get(route.course(self.course_id).homework(self.uid))
            self._detail = parser.parse_homework_detail(r)
        return self._detail

    @property
    def handins(self):
        if not hasattr(self, '_handins'):
            r = session.get(route.course(self.course_id).homework_handin_list(self.uid))
            is_group = self.detail['extra']['屬性'] == '分組作業'  # or '個人作業'
            self._handins = ItemContainer(
                parser.parse_homework_handin_list(r, is_group),
                Handin, {'course_id': self.course_id, 'is_group': is_group})
        return self._handins

    def score_handins(self, score_map):
        for handin in self.handins[1:2]:
            try:
                account = handin.account_id
                if handin.is_group:
                    account = re.findall('\d+', account)[0]
                score = score_map[account]
                result = handin.set_score(score)
                print(handin, result.json()['ret']['msg'])
            except KeyError:
                print('缺少 %s 的分數' % handin.account_id)
            except Exception as e:
                print('Catch exception', e, 'while scoring', handin)

    def download_handins(self, root_folder):
        meta_path = os.path.join(root_folder, 'meta.json')
        done_lut = json_load(meta_path)
        try:
            for handin in self.handins:
                metadata = done_lut.get(handin.id)
                if (metadata
                   and metadata.get('last_update')
                   and handin.date_string >= metadata['last_update']):
                    continue
                print(handin)
                handin.download(root_folder=root_folder)
                done_lut[handin.id] = {'last_update': handin.date_string}
        except Exception as e:
            print('Catch exception', e, 'while downloading')
        finally:
            json_dump(done_lut, meta_path)

    def __str__(self):
        return '<Homework: %s>' % (self.title)


class Material(Item):

    @property
    def detail(self):
        if not hasattr(self, '_detail'):
            r = session.get(route.course(self.course_id).document(self.uid))
            self._detail = parser.parse_material_detail(r)
        return self._detail

    def download(self, root_folder):
        folder_name = os.path.join(root_folder, '%s' % self.標題)
        if check_is_download(folder_name, ['*.pdf', '*.ppt', '*.pptx']):
            return
        for target in self.detail:
            download(target['id'], folder=folder_name)

    def __str__(self):
        return '<Material: %s, %s hits>' % (self.標題, self.人氣)


class Course(Item):

    def get_homeworks(self):
        r = session.get(route.course(self.uid).homework())
        self.homeworks = ItemContainer(
            parser.parse_homework_list(r),
            Homework, {'course_id': self.uid}
        )
        return self.homeworks

    def get_materials(self, download=False):
        r = session.get(route.course(self.uid).document())
        self.materials = ItemContainer(
            parser.parse_material_list(r),
            Material, {'course_id': self.uid}
        )
        return self.materials

    def get_forum_list(self, page=1):
        resp = session.get(
            route.course(self.uid).forum() + '&page=%d' % page)
        return parser.parse_forum_list(resp.text)

    def get_group_list(self):
        resp = session.get(
            route.course(self.uid).forum() + '&page=%d' % page)
        return parser.parse_group_list(resp.text)

    def __str__(self):
        return '<Course: %s %s>' % (self.course_id, self.name.get('zh'))


class Core():

    def __init__(self, user):
        self.user = user
        self._courses = None
        self._all_courses = None

    @property
    def courses(self) -> ItemContainer:
        if self._courses is None:
            r = session.get(route.home)
            parsed = parser.parse_course_list(r)
            self._courses = ItemContainer(parsed, Course)
        return self._courses

    @property
    def all_courses(self) -> dict:
        if self._all_courses is None:
            r = session.get('%s?f=allcourse' % route.home)
            parsed = parser.parse_all_course_list(r)
            self._all_courses = {
                key: ItemContainer(cous, Course)
                for key, cous in parsed.items()
            }
        return self._all_courses

    def get_post_detail(self, post_id):
        resp = session.post(route.post, data={'id': post_id})
        return parser.parse_post_detail(resp.json())


def download(attach_id, folder='download'):
    resp = session.get(route.attach.format(attach_id=attach_id), stream=True)
    stream_download(resp, folder)
