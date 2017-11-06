# coding=utf-8

from tornado.stack_context import StackContext

from .util import Utils
from .struct import Ignore, ThreadDict, Const


class ContextManager():

    def __enter__(self):

        return self

    def __exit__(self, *args):

        self._context_release()

        if(args[0] is Ignore):

            return True

        elif(args[1]):

            Utils.log.exception(args[1], exc_info=args[2])

            return True

    def __del__(self):

        self._context_release()

    def _context_release(self):

        Utils.log.debug(r'nothing to release')


class Transaction(ContextManager):

    def __init__(self, *callables):

        self._callables = set(_callable for _callable in callables)

    def _context_release(self):

        self.rollback()

    def add(self, _callable, *arg, **kwargs):

        self._callables.add(Utils.func_partial(_callable, *arg, **kwargs))

    def commit(self):

        if(self._callables is None):
            return

        self._callables.clear()
        self._callables = None

    def rollback(self):

        if(self._callables is None):
            return

        for _callable in self._callables:
            _callable()

        self._callables.clear()
        self._callables = None


class ContextLocal():

    _contexts = ThreadDict()

    def __init__(self):

        self._previous = []

    @classmethod
    def current(cls):

        return cls._contexts.data.get(cls.__name__, None)

    def __enter__(self):

        cls = type(self)

        context = cls._contexts.data.get(cls.__name__, None)

        self._previous.append(context)

        cls._contexts.data[cls.__name__] = self

    def __exit__(self, *args):

        cls = type(self)

        cls._contexts.data[cls.__name__] = self._previous.pop()

    def __call__(self):

        return self


class ContextResource(ContextLocal):

    def __init__(self):

        super().__init__()

        self._data = Const()

        self.cache_client = None
        self.db_client_ro = None
        self.db_client_rw = None

    @classmethod
    def has(self, key):

        context = self.current()

        if(context is None):
            return False

        return key in context._data

    @classmethod
    def get(self, key, default=None):

        context = self.current()

        if(context is None):
            return default

        return context._data.get(key, default)

    @classmethod
    def set(self, key, value):

        context = self.current()

        if(context is None):
            return False

        context._data[key] = value

        return True

    @property
    def data(self):

        return self._data


def run_with_context_resource(func, *args, **kwargs):

    with StackContext(ContextResource()):
        return func(*args, **kwargs)
