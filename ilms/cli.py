import argparse

import ilms
from ilms.core import User, Core as iLms
from ilms.utils import get_account

parser = argparse.ArgumentParser()
parser.add_argument(
    'action', help=('login / download / view'))
parser.add_argument(
    '--courses', action='store_true', help='List all courses in this semester.')
parser.add_argument(
    '-c', '--course_id', type=str, help='Specific course to view.')
parser.add_argument(
    '-V', '--version', action='version', version=ilms.__version__)


def print_course_list(ilms):
    for cou in ilms.get_courses():
        print(cou)


def main(args=None):
    args = args or parser.parse_args()

    _account, _password = get_account()
    user = User(_account, _password)
    assert user.login()

    ilms = iLms(user)

    if args.courses:
        print_course_list(ilms)


# ilms download handin --course_id CS35700 --homework Homework1
# ilms download handin --course_id CS35700 --homework Homework1 --student 10502561 / 陳xx
# ilms download material --course_id CS35700 --num 5
