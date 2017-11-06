# coding=utf-8

import functools

from unittest import skip, TextTestRunner, defaultTestLoader
from unittest.runner import _WritelnDecorator

from tornado.ioloop import IOLoop
from tornado.testing import gen_test, AsyncTestCase

from config import Config

from util.util import Utils
from util.context import run_with_context_resource


skip = skip


def engine(func):

    @functools.wraps(func)
    def __wrapper(*args, **kwargs):

        return run_with_context_resource(gen_test(func), *args, **kwargs)

    return __wrapper


class TestProgram:

    def __init__(self, modules, verbosity=2, failfast=False, logfile=None):

        self._suite = defaultTestLoader.loadTestsFromNames(modules)
        self._runner = TextTestRunner(verbosity=verbosity, failfast=failfast)

        self._logfile = logfile

    def __call__(self):

        return self.run()

    def _run(self):

        result = self._runner.run(self._suite)

        return result.wasSuccessful()

    def run(self):

        if(self._logfile):

            with open(self._logfile, r'w+') as stream:
                self._runner.stream = _WritelnDecorator(stream)
                return self._run()

        else:

            return self._run()


class TestCase(AsyncTestCase):

    utils = Utils

    def get_new_ioloop(self):

        return IOLoop.instance()

    def fetch_url(self, url, params=None, method=r'GET', *, headers=None, body=None):

        return self.utils._fetch_url(r'{0:s}{1:s}'.format(Config.TestServerHost, url), params, method, headers=headers, body=body)

    def compare_dict(self, source, target):

        for key, val in source.items():
            if(key not in target or target[key] != val):
                return False
        else:
            return True

    def compare_list(self, source, target):

        for val in source:
            if(target.index(val) < 0):
                return False
        else:
            return True
