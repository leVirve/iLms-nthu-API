import csv
import getpass
import glob
import json
import os
import pickle
import re
import sys
import urllib.parse
import zipfile

import tqdm

import ilms

mime_filename_pattern = re.compile('.*?filename="(.+)"')


def get_account():
    if os.path.exists(ilms._config_file):
        _config = json.load(open(ilms._config_file))
        _account = _config.get('account')
        _password = _config.get('password')
        if _account and _password:
            return _account, _password

    _config = {'account': input('iLMS account: '),
               'password': getpass.getpass(prompt='Password: ')}
    _account = _config.get('account')
    _password = _config.get('password')
    with open(ilms._config_file, 'w') as f:
        f.write(json.dumps(_config, indent=4))

    return _account, _password


def remove_account_file():
    if os.path.exists(ilms._config_file):
        os.remove(ilms._config_file)


def unzip_all(folder_name):
    for zip_file in glob.glob('%s/*.zip' % folder_name):
        unzip(zip_file, folder_name)


def unzip(filepath, dest_folder):
    if filepath.endswith('.zip'):
        zip_ref = zipfile.ZipFile(filepath, 'r')
        zip_ref.extractall(dest_folder)
        zip_ref.close()


def check_is_download(folder, file_types):
    files = []
    for ftype in file_types:
        files.extend(glob.glob('%s/%s' % (folder, ftype)))
    return files


def get_home_dir():
    _base_dir = os.path.expanduser('~')
    _ilms_dir = os.path.join(_base_dir, '.ilms')
    return _ilms_dir


def save_session(sess):
    base = ilms._ilms_dir
    with open(os.path.join(base, 'sess.pickle'), 'wb') as f:
        pickle.dump(sess, f, pickle.HIGHEST_PROTOCOL)


def load_session():
    base = ilms._ilms_dir
    filepath = os.path.join(base, 'sess.pickle')
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def json_load(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        return {}


def json_dump(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def load_score_csv(filepath):
    with open(filepath, newline='', encoding='utf8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        rows = [row for row in spamreader]

        score_map = {}
        for entry in rows:
            assert len(entry) == 2
            student_id, score = entry
            score_map[student_id] = float(score)

        return score_map


def stream_download(r, folder='download'):
    filesize = int(r.headers['content-length'])
    filename = r.headers['content-disposition']
    filename = mime_filename_pattern.match(filename).group(1)

    os.makedirs(folder, exist_ok=True)
    filename = urllib.parse.unquote(filename)
    path = os.path.join(folder, filename)

    chunk_size = 2048
    with tqdm.tqdm(total=filesize // chunk_size, ascii=True, leave=False) as p:
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                p.update(1)
    return filename


def safe_str(text):
    encoding = sys.stdout.encoding
    return text.encode(encoding, 'ignore').decode(encoding)
