import math
import pprint

import click

from ilms.core import User, Core as iLms
from ilms.utils import get_account, load_score_csv


core = None


def query_helper(container, **kwarg):
    key, value = list(kwarg.items())[0]
    if not value:
        value = input('%s: ' % key)
    return container.find(**{key: value})


def _find_course(ilms, semester_id, course_id):
    if semester_id is None:
        cou = query_helper(ilms.courses, course_id=course_id)
    else:
        cou = query_helper(ilms.all_courses[semester_id],
                           course_id=course_id)
    if cou is None:
        for sem, courses in ilms.all_courses.items():
            cou = query_helper(courses, course_id=course_id)
            if cou:
                break
    return cou


@click.command()
@click.argument('func')
@click.option('--semester_id', default=None, help='學期')
@click.option('--course_id', default='', help='課號關鍵字')
@click.option('--verbose', is_flag=True, help='顯示詳細資訊')
def view(func, semester_id, course_id, verbose):
    ''' 選擇查詢項目 課程 / 作業 / 上課教材 ['course', 'homework', 'material']
    '''

    def print_course_list(ilms):
        if semester_id is None:
            for cou in ilms.courses:
                print(cou)
            return
        if semester_id == 'all':
            for sem, courses in ilms.all_courses.items():
                print('-- %s --' % sem)
                for cou in courses:
                    print(cou)
        else:
            for cou in ilms.all_courses[semester_id]:
                print(cou)

    def print_homework_list(ilms):
        cou = _find_course(ilms, semester_id, course_id)
        for hw in cou.get_homeworks():
            verbose and pprint.pprint(hw.detail) or print(hw)

    def print_material_list(ilms):
        cou = _find_course(ilms, semester_id, course_id)
        for mat in cou.get_materials():
            verbose and pprint.pprint(mat.detail) or print(mat)

    {
        'course': print_course_list,
        'homework': print_homework_list,
        'material': print_material_list,
    }[func](core)


@click.command()
@click.argument('name')
@click.option('--course_id', default='', help='課號關鍵字')
@click.option('--course', default='', help='課程名稱關鍵字')
@click.option('--hw_title', default='', help='作業標題')
@click.option('--folder', default='', help='下載至...資料夾')
def download(name, course_id, course, hw_title, folder):
    ''' 選擇下載項目 上課教材 / 繳交作業 (助教) ['material', 'handin']
    '''

    def download_handins(ilms):
        cou = _find_course(ilms, None, course_id)
        hw = query_helper(cou.get_homeworks(), title=hw_title)
        root_folder = folder or 'download/%s/' % hw.title
        print(hw, '-> into', root_folder)
        hw.download_handins(root_folder)
        # if more specific options to download single file

    def download_materials(ilms):
        cou = _find_course(ilms, None, course_id)
        cou = cou or ilms.courses.find(name=course)
        for material in cou.get_materials():
            root_folder = folder or 'download/%s/' % cou.course_id
            print(material, '-> into', root_folder)
            material.download(root_folder=root_folder)

    {
        'handin': download_handins,
        'material': download_materials,
    }[name](core)


@click.command()
@click.option('--course_id', default='', help='課號關鍵字')
@click.option('--hw_title', default='', help='作業標題')
@click.option('--csv', default='', help='CSV 成績表')
def score(course_id, hw_title, csv):

    cou = _find_course(core, None, course_id)
    hw = query_helper(cou.get_homeworks(), title=hw_title)

    score_map = load_score_csv(csv or input('Path to csv sheet: '))
    score_map = {
        student_id: math.ceil(score)
        for student_id, score in score_map.items()}

    hw.score_handins(score_map)


@click.group()
def main(args=None):
    _account, _password = get_account()
    user = User(_account, _password)
    assert user.login()

    global core
    core = iLms(user)


main.add_command(view)
main.add_command(score)
main.add_command(download)
