# coding=utf-8

import functools
from contextlib import contextmanager

from tornado.gen import coroutine, Return
from tornado.concurrent import Future

from .struct import Ignore
from .util import Utils
from .database import safestr


def share_future(func):

    __future = {}

    def __wrapper(*args, **kwargs):

        result = None

        func_sign = Utils.params_sign(func, *args, **kwargs)

        if func_sign in __future:

            result = Future()

            __future[func_sign].append(result)

        else:

            result = coroutine(func)(*args, **kwargs)

            __future[func_sign] = [result]

            result.add_done_callback(Utils.func_partial(__clear_future, func_sign))

        return result

    def __clear_future(func_sign, future):

        if func_sign not in __future:
            return

        futures = __future.pop(func_sign)

        result = futures.pop(0).result()

        for future in futures:
            future.set_result(Utils.deepcopy(result))

    return __wrapper


def sql_safe_params(func):

    @functools.wraps(func)
    def __wrapper(*args, **kwargs):

        if args:
            args = [safestr(val) if(isinstance(val, str)) else val for val in args]

        if kwargs:
            kwargs = {key: safestr(val) if(isinstance(val, str)) else val for key, val in kwargs.items()}

        return func(*args, **kwargs)

    return __wrapper


@contextmanager
def catch_error(quiet=False):

    try:

        yield

    except Return as err:

        raise err

    except Ignore as err:

        pass

    except Exception as err:

        if quiet:
            Utils.log.debug(err)
        else:
            Utils.log.exception(err)

from tornado.gen import coroutine, Return, is_coroutine_function

def run_in_executor(threadpool_executor, func):

    @coroutine
    def wrapper(*args, **kwargs):

        func_result = yield threadpool_executor.submit(func, *args, **kwargs)

        if is_coroutine_function(func):
            result = yield func_result
        else:
            result = func_result

        return result

    return wrapper

