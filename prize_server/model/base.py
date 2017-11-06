# coding=utf-8

import functools
import aiomysql
import pytds
from tornado.gen import coroutine, sleep
from tornado.log import app_log

from config import Config
from util.struct import Ignore
from util.util import Singleton, Utils
from util.cache import MCachePool as MCachePoolABC, config_redis_default
from util.mem_cache import func_cache as original_func_cache
from util.database import MySQLPoolABC



class MCachePool(Singleton, MCachePoolABC):

    def __init__(self):

        addr = Config.RedisHost

        settings = {
            r'db': Config.RedisBase,
            r'minsize': Config.RedisMinConn,
            r'maxsize': Config.RedisMaxConn,
            r'password': Config.RedisPasswd
        }

        MCachePoolABC.__init__(self, addr, settings)


class MySQLPool(Singleton, MySQLPoolABC):

    def __init__(self):

        addr = Config.MySqlMaster

        settings = {
            r'user': Config.MySqlUser,
            r'password': Config.MySqlPasswd,
            r'minsize': Config.MySqlMinConn,
            r'maxsize': Config.MySqlMaxConn,
            r'db': Config.MySqlDbName,
            r'charset': r'utf8',
            r'cursorclass': aiomysql.DictCursor,
        }

        MySQLPoolABC.__init__(self, addr, **settings)


@coroutine
def initialize():

    Utils._HTTP_ERROR_AUTO_RETRY = Config.HttpErrorAutoRetry
    Utils._HTTP_CONNECT_TIMEOUT = Config.HttpConnectTimeout
    Utils._HTTP_REQUEST_TIMEOUT = Config.HttpRequestTimeout

    yield MySQLPool().initialize()
    yield MCachePool().initialize()

    config_redis_default(expire=Config.RedisExpires, key_prefix=r'account_service__')


class BaseModel(Singleton, Utils):

    def __init__(self):

        self._db_pool = MySQLPool()

        self._cache_pool = MCachePool()

    def get_db_client(self, readonly=False):

        return self._db_pool.get_client(readonly)

    def get_db_transaction(self):

        return self._db_pool.get_transaction()

    def get_mssql_conn(self, database_name):

        host, port = Config.MssqlHost

        conn = pytds.connect(host, database_name, Config.MssqlUser, Config.MssqlPasswd, port=port, as_dict=True)

        # mssql log
        app_log.info(r'mssql connect to {}'.format(database_name))
        def conn_close(conn):
            type(conn).close(conn)
            app_log.info(r'mssql conn closed')
        import functools
        conn.close = functools.partial(conn_close, conn)

        return conn

    def get_cache_client(self):

        return self._cache_pool.get_client()

    def Break(self, msg=None):

        raise Ignore(msg)

    @coroutine
    def acquire_lock(self, key, retry_interval=0.1, max_hold_time=Config.DistributedLockMaxHoldTime, timeout=Config.AcquireDistributedLockTimeout):
        """
        key: 分布式锁唯一标示
        retry_interval: 尝试获取锁的时间间隔
        max_hold_time: 最长持有时间，超时自动释放，为防止极端情况下锁被永久持有的问题
        timeout: 获取锁超时时间

        使用样例:

            # self 是BaseModel实例

            lname = r'some_lock_name'

            lock = yield self.acquire_lock(lname)

            if lock:
                try:
                    yield sleep(5)
                    1 / 0
                    yield sleep(5)
                finally:
                    yield self.release_lock(lname)
            else:
                pass

        """

        app_log.debug(r'try acquire lock {}'.format(key))

        cache = self.get_cache_client()

        acquire_time_total = 0
        timeout_time = 0
        begin_time = self.timestamp()

        while not (yield cache.setnx(key, self.timestamp())):

            acquire_time_total += retry_interval

            if acquire_time_total > timeout:

                timeout_time = self.timestamp()

                break

            yield sleep(retry_interval)

        if timeout_time:

            app_log.warning(r'acquire lock {} timeout, cost {} s'.format(key, timeout_time - begin_time))

            return False

        app_log.debug(r'acquire lock success {}'.format(key))

        yield cache.expire(key, max_hold_time)

        return True

    @coroutine
    def release_lock(self, key):

        cache = self.get_cache_client()

        yield cache.delete(key)

        app_log.debug(r'release lock {}'.format(key))

