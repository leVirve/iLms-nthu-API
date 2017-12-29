import math
import pprint

import click

from ilms.core import User, Core as iLms
from ilms.utils import get_account, load_score_csv


core = None


@click.command()
@click.argument('name')
@click.option('--course_id', default='')
@click.option('--verbose', is_flag=True)
def view(name, course_id, verbose):

    def print_course_list(ilms):
        for cou in ilms.get_courses():
            print(cou)

    def print_homework_list(ilms):
        cou = ilms.get_courses().find(course_id=course_id)
        for hw in cou.get_homeworks():
            verbose and pprint.pprint(hw.detail) or print(hw)

    {
        'course': print_course_list,
        'homework': print_homework_list,
    }[name](core)


@click.command()
@click.argument('name')
@click.option('--course_id', default='')
@click.option('--course', default='')
@click.option('--hw_title', default='')
@click.option('--folder', default='')
def download(name, course_id, course, hw_title, folder):

    def download_handins(ilms):
        cou = ilms.get_courses().find(course_id=course_id)
        hw = cou.get_homeworks().find(title=hw_title)
        root_folder = folder or 'download/%s/' % hw.title
        print(hw, '-> into', root_folder)
        hw.download_handins(root_folder)
        # if more specific options to download single file

    def download_materials(ilms):
        cou = ilms.get_courses().find(course_id=course_id)
        cou = cou or ilms.get_courses().find(name=course)
        for material in cou.get_materials():
            root_folder = folder or 'download/%s/' % cou.course_id
            print(material, '-> into', root_folder)
            material.download(root_folder=root_folder)

    {
        'handin': download_handins,
        'material': download_materials,
    }[name](core)


@click.command()
@click.option('--course_id', default='')
@click.option('--hw_title', default='')
@click.option('--score_csv', default='')
def score(course_id, hw_title, score_csv):

    cou = core.get_courses().find(course_id=course_id)
    hw = cou.get_homeworks().find(title=hw_title)

    score_map = load_score_csv(score_csv)
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
