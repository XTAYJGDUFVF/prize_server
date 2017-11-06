# coding=utf-8

import sys
import json
import threading
import configparser

from collections import OrderedDict

from .util import Utils


class Ignore(Exception):

    def __init__(self, msg=None):

        if msg:
            Utils.log.warning(msg)


class NullData():

    def __int__(self):

        return 0

    def __float__(self):

        return 0.0

    def __len__(self):

        return 0

    def __repr__(self):

        return r''

    def __eq__(self, obj):

        return bool(obj) == False

    def __nonzero__(self):

        return False

    def __cmp__(self, val):

        if val is None:
            return 0
        else:
            return 1


class ErrorData(NullData):

    __slots__ = [r'data']

    def __init__(self, data=None):

        self.data = data if isinstance(data, str) else str(data)

    def __repr__(self):

        return self.data


class ThreadList(threading.local):

    __slots__ = [r'data']

    def __init__(self):

        self.data = []


class ThreadDict(threading.local):

    __slots__ = [r'data']

    def __init__(self):

        self.data = {}


class Const(OrderedDict):

    class Predefine(NullData):
        pass

    class ConstError(TypeError):
        pass

    def __init__(self):

        super().__init__()

    def __getattr__(self, key):

        if key[:1] == r'_':
            return super().__getattr__(key)
        else:
            return self.__getitem__(key)

    def __setattr__(self, key, val):

        if key[:1] == r'_':
            super().__setattr__(key, val)
        else:
            self.__setitem__(key, val)

    def __delattr__(self, key):

        if key[:1] == r'_':
            super().__delattr__(key)
        else:
            self.__delitem__(key)

    def __setitem__(self, key, val):

        if key in self and not isinstance(self.__getitem__(key), self.Predefine):
            raise self.ConstError()
        else:
            super().__setitem__(key, val)

    def __delitem__(self, key):

        raise self.ConstError()

    def exist(self, val):

        return val in self.values()


class ConfigParser(configparser.ConfigParser):

    def getstr(self, section, option, default=None, **kwargs):

        val = self.get(section, option, **kwargs)

        return val if val else default

    def getjson(self, section, option, **kwargs):

        val = self.get(section, option, **kwargs)

        result = json.loads(val)

        return result

    def _split_host(self, val):

        host, port = val.split(r':', 2)

        return host.strip(), int(port.strip())

    def get_split_host(self, section, option, **kwargs):

        val = self.get(section, option, **kwargs)

        return self._split_host(val)

    def _split_str(self, val, sep=r'|'):

        result = tuple(temp.strip() for temp in val.split(sep))

        return result

    def get_split_str(self, section, option, sep=r'|', **kwargs):

        val = self.get(section, option, **kwargs)

        return self._split_str(val, sep)

    def _split_int(self, val, sep=r','):

        result = tuple(int(temp.strip()) for temp in val.split(sep))

        return result

    def get_split_int(self, section, option, sep=r',', **kwargs):

        val = self.get(section, option, **kwargs)

        return self._split_int(val, sep)

    def split_float(self, val, sep=r','):

        result = tuple(float(item.strip()) for item in val.split(sep))

        return result

    def get_split_float(self, section, option, sep=r',', **kwargs):

        val = self.get(section, option, **kwargs)

        return self.split_float(val, sep)


class Configure(Const):

    def __init__(self):

        super().__init__()

        self._parser = ConfigParser()

    def _init_options(self):

        self.clear()

    def get_option(self, section, option):

        return self._parser.get(section, option)

    def get_options(self, section):

        parser = self._parser

        options = {}

        for option in parser.options(section):
            options[option] = parser.get(section, option)

        return options

    def set_options(self, section, **options):

        if not self._parser.has_section(section):
            self._parser.add_section(section)

        for option, value in options.items():
            self._parser.set(section, option, value)

        self._init_options()

    def read(self, files):

        self._parser.clear()
        self._parser.read(files, r'utf-8')

        self._init_options()

    def read_str(self, val):

        self._parser.clear()
        self._parser.read_string(val)

        self._init_options()

    def read_dict(self, val):

        self._parser.clear()
        self._parser.read_dict(val)

        self._init_options()


PY3 = sys.version_info[0] == 3

if PY3:
    def _iteritems(d, **kwargs):
        return iter(d.items(**kwargs))
else:
    def _iteritems(d, **kwargs):
        return iter(d.iteritems(**kwargs))


class OptionalDict(dict):

    """A dictionary only store non none values"""
    def __init__(self, *args, **kwargs):

        # XXX
        super().__init__()

        self.update(*args, **kwargs)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        if value is None:
            return
        return dict_setitem(self, key, value)

    def update(self, *args, **kwargs):
        for k, v in _iteritems(dict(*args, **kwargs)):
            self[k] = v

    def setdefault(self, k, d=None, dict_setdefault=dict.setdefault):
        if d is None:
            return
        return dict_setdefault(self, k, d)


optionaldict = OptionalDict
