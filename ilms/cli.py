import os
import json
import getpass
import argparse

import ilms
from ilms.core import User, Core as iLms

parser = argparse.ArgumentParser()
parser.add_argument(
    'action', help=('login / download / view'))
parser.add_argument(
    '--courses', action='store_true', help='List all courses in this semester.')
parser.add_argument(
    '-c', '--course_id', type=str, help='Specific course to view.')
parser.add_argument(
    '-V', '--version', action='version', version=ilms.__version__)


def get_account():
    global _account, _password
    _config = {'account': input('iLms account:'),
               'password': getpass.getpass(prompt='Password:')}
    _account = _config.get('account')
    _password = _config.get('password')
    with open(_config_file, 'w') as f:
        f.write(json.dumps(_config, indent=4))


_config_file = os.path.expanduser(os.path.join(ilms._ilms_dir, 'ilms.json'))

if os.path.exists(_config_file):
    _config = json.load(open(_config_file))
    _account = _config.get('account')
    _password = _config.get('password')
    if not _account or not _password:
        get_account()

if not os.path.exists(_config_file):
    get_account()


def print_course_list(ilms):
    for cou in ilms.get_courses():
        print(cou)


def main(args=None):
    args = args or parser.parse_args()

    user = User(_account, _password)
    assert user.login()

    ilms = iLms(user)

    if args.courses:
        print_course_list(ilms)
