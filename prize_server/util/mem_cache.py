# coding=utf-8

"""
requirements:
1. 用当前项目的coroutine, 替换本文件的coroutine
2. 用当前项目的Future, 替换本文件的Future

"""

import time
import hashlib

from tornado.gen import coroutine, Future


def _timestamp():
    return int(time.time())


def _params_sign(*args, **kwargs):

    result = []

    if args:
        result.extend(str(val) for val in args)

    if kwargs:

        kwargs_part = r'&'.join(r'{0}={1}'.format(key, val) for key, val in sorted(kwargs.items(), key=lambda x: x[0]))

        result.append(kwargs_part)

    raw_str = r'&'.join(result)

    raw_b = bytes(raw_str, r'utf-8')

    return hashlib.md5(raw_b).hexdigest()


class TimedCache(object):

    def __init__(self, ttl=0):

        self._ttl = ttl
        self._data = dict()

    def get(self, key):

        result = None

        if key in self._data:

            item = self._data[key]

            if item[0] > _timestamp():
                result = item[1]
            else:
                del self._data[key]

        return result

    def set(self, key, val, expire=0):

        if expire <= 0:
            expire = self._ttl

        now_time = _timestamp()

        self._data[key] = (now_time + expire, val)

        del_keys = []

        for key, val in self._data.items():
            if val[0] < now_time:
                del_keys.append(key)

        for key in del_keys:
            del self._data[key]

    def delete(self, key):

        if key in self._data:
            del self._data[key]

    def exists(self, key):

        result = False

        if key in self._data:

            item = self._data[key]

            if item[0] > _timestamp():
                result = True
            else:
                del self._data[key]

        return result

    def size(self):

        length = 0

        now_time = _timestamp()

        del_keys = []

        for key, val in self._data.items():
            if val[0] > now_time:
                length += 1
            else:
                del_keys.append(key)

        for key in del_keys:
            del self._data[key]

        return length


def func_cache(expire, func):

    __cache = TimedCache()

    def __wrapper(*args, **kwargs):

        func_sign = _params_sign(func, *args, **kwargs)

        result = __cache.get(func_sign)

        if result is None:

            result = func(*args, **kwargs)

            if isinstance(result, Future):
                result = yield result

            __cache.set(func_sign, result, expire)

        return result

    return coroutine(__wrapper)
