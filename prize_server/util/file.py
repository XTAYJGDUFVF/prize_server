# coding=utf-8

from tornado.gen import coroutine

from .util import Utils
from .cache import TimedCache


class FileLoaderABC(Utils):

    def __init__(self, file_cache_expire):

        self._files = TimedCache(file_cache_expire)
        self._futures = {}

    # to override
    # @thread_worker
    def _load(self, file_path):

        with open(file_path, r'rb') as file:
            return file.read()

    @coroutine
    def load(self, file_path):

        if(self._files.exists(file_path)):
            return self._files.get(file_path)

        if(file_path in self._futures):
            return (yield self._futures[file_path])

        future = self._futures[file_path] = self._load(file_path)

        result = yield future

        del self._futures[file_path]

        if(result):
            self._files.set(file_path, result)

        return result

    @coroutine
    def _load_url(self, file_url):

        return (yield self.fetch_url(file_url, method=r'GET', style=r'BYTES'))

    @coroutine
    def load_url(self, file_url):

        if(self._files.exists(file_url)):
            return self._files.get(file_url)

        if(file_url in self._futures):
            return (yield self._futures[file_url])

        future = self._futures[file_url] = self._load_url(file_url)

        result = yield future

        del self._futures[file_url]

        if(result):
            self._files.set(file_url, result)

        return result
