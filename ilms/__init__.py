import os


_base_dir = os.path.expanduser('~')
_ilms_dir = os.path.join(_base_dir, '.ilms')
if not os.path.exists(_ilms_dir):
    os.makedirs(_ilms_dir)

_config_file = os.path.expanduser(os.path.join(_ilms_dir, 'ilms.json'))

__version__ = '0.0.5'
