import os.path
import json
from codecs import open as copen
import logging
from datetime import datetime

from common.exceptions import ConfigurationError


def resolve_dict(parent_dict, dotted_str):
    if '.' in dotted_str:
        keys = dotted_str.split('.')
        data = parent_dict

        for k in keys:
            data = data[k]

        return data
    return parent_dict[dotted_str]

def timestamp(format='%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(format)


class Printable(object):
    _tname: str = 'null'


    def print(self, pl, *args, **kwargs):
        return print('[{}] ({}) {}'.format(timestamp(), self._tname, pl), *args, **kwargs)

    def debug(self, pl, *args, **kwargs):
        logging.debug('[{}] {}'.format(self._tname, pl))
        return self.print('\033[94m{}\033[0m'.format(pl), *args, **kwargs)

    def info(self, pl, *args, **kwargs):
        logging.info('[{}] {}'.format(self._tname, pl))
        return self.print(pl, *args, **kwargs)

    def warning(self, pl, *args, **kwargs):
        logging.warning('[{}] {}'.format(self._tname, pl))
        return self.print('\033[93mWARN: {}\033[0m'.format(pl), *args, **kwargs)

    def error(self, pl, *args, **kwargs):
        logging.error('[{}] {}'.format(self._tname, pl))
        return self.print('\033[91mERR: {}\033[0m'.format(pl), *args, **kwargs)


class Config(object):

    _path = None
    _config = None

    def __init__(self, path):
        self.setPath(path)
        self.initialize()

    def initialize(self):
        if self._path is None:
            raise ConfigurationError('Config path not specified.')

        self.load()

    def setPath(self, path):
        if os.path.isfile(path):
            self._path = path
        else:
            raise ConfigurationError('Config file at "{}" not found.'.format(path))

    def save(self):
        with copen(self._path, 'w', 'utf-8') as f:
            json.dump(self._config, f, indent=4, sort_keys=True)

    def load(self):
        with copen(self._path, 'r', 'utf-8') as f:
            try:
                self._config = json.load(f)
            except json.decoder.JSONDecodeError as m:
                raise ConfigurationError('Invalid config file format: {}'.format(m))

    def get(self, key):
        return resolve_dict(self._config, key)

    def set(self, key, value):
        def put(d, keys, item):
                if "." in keys:
                    key, rest = keys.split(".", 1)
                    if key not in d:
                        d[key] = {}
                    put(d[key], rest, item)
                else:
                    d[keys] = item

        put(self._config, key, value)

        self.save()
