# coding=utf-8

from tornado.gen import sleep, coroutine, is_coroutine_function, isawaitable
from tornado.log import app_log
from tornado.ioloop import IOLoop


class RepeatTask(object):

    def __init__(self, interval, _callable, *args, **kw_args):

        self.interval = interval

        self.callable = _callable

        self.args = args

        self.kw_args = kw_args

        self._stop = False

    def wrapped_callable(self, _callable, *args, **kw_args):
        """
        wrap any kind of callable into chained callable, which will call itself after certain interval
        """

        if is_coroutine_function(_callable):

            @coroutine
            def wrapper():
                try:
                    yield _callable(*args, **kw_args)
                except Exception as e:
                    app_log.exception(r'{}'.format(e))
                if not self._stop:
                    yield sleep(self.interval)
                    loop = IOLoop.current()
                    loop.call_later(0, wrapper)
            return wrapper

        else:

            def wrapper():
                try:
                    _callable(*args, **kw_args)
                except Exception as e:
                    app_log.exception(r'{}'.format(e))
                if not self._stop:
                    loop = IOLoop.current()
                    loop.call_later(self.interval, wrapper)
            return wrapper


    @coroutine
    def run(self):
        """
        run coroutine or normal function all in coroutine style
        """

        func_like = self.wrapped_callable(self.callable, *self.args, **self.kw_args)

        coro_like = func_like()

        if isawaitable(coro_like):
            yield coro_like

    def stop(self):

        self._stop = True
