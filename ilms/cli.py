import math
import pprint
from functools import partial

import click

from ilms.core import User, Core as iLms
from ilms.utils import get_account, load_score_csv, remove_account_file


def aquire_core():
    _account, _password = get_account()
    user = User(_account, _password)
    assert user.login()
    return iLms(user)


def query_helper(container, query, prompt):
    key, value = list(query.items())[0]
    if not value:
        value = input('%s: ' % prompt)
        for k, v in query.items():
            query[k] = value
    return container.find(**query)


def _heuristic_find_course(ilms, semester_id, course_kw):
    possible_query = {'course_id': course_kw, 'name': course_kw}
    _find_course = partial(query_helper, query=possible_query, prompt='輸入課程關鍵字')

    if semester_id:
        cou = _find_course(ilms.all_courses[semester_id])
    else:
        cou = _find_course(ilms.courses)

        if cou is None:
            for sem, courses in ilms.all_courses.items():
                cou = _find_course(courses)
                if cou:
                    break

    ''' No such course '''
    if cou is None:
        print('查無此課程!')
        exit()

    print('\n=== 課程 ===\n', cou)
    return cou


@click.command()
@click.argument('name')
@click.option('--semester_id', default=None, help='學期')
@click.option('--course', default='', help='課號關鍵字')
@click.option('--verbose', is_flag=True, help='顯示詳細資訊')
def view(name, semester_id, course, verbose):
    ''' 選擇查詢項目 課程 / 作業 / 上課教材
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
        cou = _heuristic_find_course(ilms, semester_id, course)
        for hw in cou.get_homeworks():
            verbose and pprint.pprint(hw.detail) or print(hw)

    def print_material_list(ilms):
        cou = _heuristic_find_course(ilms, semester_id, course)
        for mat in cou.get_materials():
            verbose and pprint.pprint(mat.detail) or print(mat)

    core = aquire_core()
    {
        'course': print_course_list,
        'homework': print_homework_list,
        'material': print_material_list,
    }[name](core)


@click.command()
@click.argument('name')
@click.option('--course', default='', help='課程關鍵字')
@click.option('--hw_title', default='', help='作業標題')
@click.option('--folder', default='', help='下載至...資料夾')
def download(name, course, hw_title, folder):
    ''' 選擇下載項目 上課教材 / 繳交作業 (助教)
    '''

    def download_handins(ilms):
        cou = _heuristic_find_course(ilms, None, course)
        hw = query_helper(cou.get_homeworks(), {'title': hw_title}, prompt='作業標題')
        root_folder = folder or 'download/%s/' % hw.title
        print(hw, '-> into', root_folder)
        hw.download_handins(root_folder)
        # if more specific options to download single file

    def download_materials(ilms):
        cou = _heuristic_find_course(ilms, None, course)
        for material in cou.get_materials():
            root_folder = folder or 'download/%s/' % cou.course_id
            print(material, '-> into', root_folder)
            material.download(root_folder=root_folder)

    core = aquire_core()
    {
        'handin': download_handins,
        'material': download_materials,
    }[name](core)


@click.command()
@click.option('--course', default='', help='課程關鍵字')
@click.option('--hw_title', default='', help='作業標題')
@click.option('--csv', default='', help='CSV 成績表')
def score(course, hw_title, csv):
    ''' 登記分數 '''
    core = aquire_core()

    cou = _heuristic_find_course(core, None, course)
    hw = query_helper(cou.get_homeworks(), title=hw_title)

    score_map = load_score_csv(csv or input('Path to csv sheet: '))
    score_map = {
        student_id: math.ceil(score)
        for student_id, score in score_map.items()}

    hw.score_handins(score_map)


@click.command()
def logout():
    ''' 登出 iLMS-NTHU API '''
    try:
        remove_account_file()
    except Exception as e:
        print('無法登出:', e)
    finally:
        print('成功登出')


@click.group()
def main():
    pass


main.add_command(view)
main.add_command(score)
main.add_command(download)
main.add_command(logout)
