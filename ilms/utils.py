import os
import glob
import pickle
import zipfile
from pip._vendor.progress.bar import ShadyBar

import ilms


class ProgressBar(ShadyBar):

    suffix = ' %(percent).1f%%'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calc_step(self, size):
        if size < 10:
            self.max = size
            return 1
        else:
            self.max = size // 10
            return 10


def unzip_all(folder_name):
    for zip_file in glob.glob('%s/*.zip' % folder_name):
        unzip(zip_file, folder_name)


def unzip(filepath, dest_folder):
    if filepath.endswith('.zip'):
        zip_ref = zipfile.ZipFile(filepath, 'r')
        zip_ref.extractall(dest_folder)
        zip_ref.close()


def check_is_download(folder):
    zip_type = ['*.zip', '*.rar']
    return any([glob.glob('%s/%s' % (folder, ztype))] for ztype in zip_type)


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


def stream_download(stream_resp, folder='download'):
    filename = stream_resp.headers['content-disposition'].split("'")[-1]
    filesize = int(stream_resp.headers['content-length'])

    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    chunk_size = 1024
    progress = ProgressBar()
    progress.max = filesize // chunk_size
    with open(path, 'wb') as f:
        for chunk in stream_resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
            progress.next()
    progress.finish()
    return filename
