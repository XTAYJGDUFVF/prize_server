# coding=utf-8

"""
requirements:
1. 用当前项目的coroutine, 替换本文件的coroutine
2. 用当前项目的log, 替换本文件的app_log

aioredis=1.1.0

"""

import pickle
import zlib

from tornado.gen import coroutine
from tornado.log import app_log
import aioredis


_DEFAULT_CONFIG = {
    r'expire': 0,
    r'key_prefix': r''
}

def config_redis_default(**config):

    _DEFAULT_CONFIG.update(config)


class MCachePool(object):

    def __init__(self, addr, settings):

        self._addr = addr

        self._settings = settings

        self._pool = None

    @coroutine
    def initialize(self):

        if self._pool is None:

            self._pool = yield aioredis.create_pool(self._addr, **self._settings)

            app_log.info(r'MCachePool initialized')

    def get_client(self):

        return CacheClient(self._pool)

    def get_conn_status(self):

        conn_status = {
            r'max_conn': self._pool.maxsize,
            r'min_conn': self._pool.minsize,
            r'conn_num': self._pool.size,
            r'idle_num': self._pool.freesize,
            r'db': self._pool.db
        }

        return conn_status


class CacheClient(object):

    def __init__(self, pool):

        self._pool = pool

    @coroutine
    def _acquire_client(self):

        client = yield self._pool.acquire()

        return client

    def _release_client(self, client):

        self._pool.release(client)

    @staticmethod
    def pickle_dumps_zip(val):

        stream = pickle.dumps(val)

        result = zlib.compress(stream)

        return result

    @staticmethod
    def unzip_pickle_loads(val):

        if val is None:
            return None

        stream = zlib.decompress(val)

        result = pickle.loads(stream)

        return result

    @coroutine
    def get(self, key):

        result = None

        key = _DEFAULT_CONFIG[r'key_prefix'] + key

        try:

            client = yield self._acquire_client()

            b_val = yield client.get(key)

            result = self.unzip_pickle_loads(b_val)

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache get: {}'.format(e))

        return result

    @coroutine
    def set(self, key, val, expire=None):

        if expire is None:
            expire = _DEFAULT_CONFIG[r'expire']

        result = None

        key = _DEFAULT_CONFIG[r'key_prefix'] + key

        try:

            client = yield self._acquire_client()

            b_val = self.pickle_dumps_zip(val)

            yield client.set(key, b_val, expire=expire)

            result = True

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache set: {}'.format(e))

        return result

    @coroutine
    def delete(self, key):

        key = _DEFAULT_CONFIG[r'key_prefix'] + key

        try:

            client = yield self._acquire_client()

            yield client.delete(key)

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache delete: {}'.format(e))

    @coroutine
    def publish(self, channel, content):

        try:

            if isinstance(content, str):
                content = bytes(content, r'utf-8')

            client = yield self._acquire_client()

            yield client.publish(channel, content)

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache publish: {}'.format(e))

    @coroutine
    def expire(self, key, expire):

        key = _DEFAULT_CONFIG[r'key_prefix'] + key

        try:

            client = yield self._acquire_client()

            yield client.expire(key, expire)

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache expire: {}'.format(e))

    @coroutine
    def ttl(self, key):

        result = 0

        key = _DEFAULT_CONFIG[r'key_prefix'] + key

        try:

            client = yield self._acquire_client()

            ttl_second = yield client.ttl(key)

            if ttl_second > 0:
                result = ttl_second

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache ttl: {}'.format(e))

        return result

    @coroutine
    def setnx(self, key, val):

        result = False

        key = _DEFAULT_CONFIG[r'key_prefix'] + key

        try:

            client = yield self._acquire_client()

            setnx_result = yield client.setnx(key, val)

            if setnx_result:
                result = True 

            self._release_client(client)

        except Exception as e:

            app_log.exception(r'cache setnx: {}'.format(e))

        return result