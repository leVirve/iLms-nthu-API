import zipfile
from pip._vendor.progress.bar import ShadyBar


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


def unzip(filepath, dest_folder):
    if filepath.endswith('.zip'):
        zip_ref = zipfile.ZipFile(filepath, 'r')
        zip_ref.extractall(dest_folder)
        zip_ref.close()
