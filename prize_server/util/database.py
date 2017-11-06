# coding=utf-8

import aiomysql

from tornado.gen import coroutine

from .util import Utils
from .struct import Ignore


class MySQLPoolABC(Utils):

    def __init__(self, address, **settings):

        self._address = address

        self._settings = settings

        self._pool = None

    @coroutine
    def initialize(self):

        if self._pool:

            return

        host, port = self._address

        self._pool = yield aiomysql.create_pool(
            **dict(self._settings, host=host, port=port, autocommit=True)
        )

        self.log.info(r'MySQL pool initialized')

    def get_client(self, readonly=False):

        result = None

        try:

            result = DBClient(self._pool, readonly)

        except Exception as err:

            self.log.exception(err)

        return result

    def get_transaction(self):

        result = None

        try:

            result = DBTransaction(self._pool)

        except Exception as err:

            self.log.exception(err)

        return result

    def get_conn_status(self):

        conn_status = {
            r'max_conn': self._pool.maxsize,
            r'min_conn': self._pool.minsize,
            r'conn_num': self._pool.size,
            r'idle_num': self._pool.freesize,
        }

        return conn_status


class SQLQuery():

    # 数据库表达式
    _exp = {
        r'eq': r'=', r'neq': r'<>', r'gt': r'>', r'egt': r'>=', r'lt': r'<', r'elt': r'<=',
        r'notlike': r'NOT LIKE', r'like': r'LIKE', r'in': r'IN', r'exp': r'EXP',
        r'notin': r'NOT IN', r'not in': r'NOT IN', r'between': r'BETWEEN', r'not between': r'NOT BETWEEN', r'notbetween': r'NOT BETWEEN',
        r'exists': r'EXISTS', r'notexists': r'NOT EXISTS', r'not exists': r'NOT EXISTS', r'null': r'NULL', r'notnull': r'NOT NULL', r'not null': r'NOT NULL'
    }

    # SQL表达式
    _select_sql = r'SELECT {distinct} {field} FROM {table}{force}{join}{where}{group}{having}{order}{limit}{lock};'
    _insert_sql = r'INSERT INTO {table} ({field}) VALUES ({data});'
    _insert_all_sql = r'INSERT INTO {table} ({field}) {data};'
    _update_sql = r'UPDATE {table} SET {set} {join} {where} {order}{limit};'
    _delete_sql = r'DELETE FROM {table} {using} {join} {where} {order}{limit};'

    @staticmethod
    def safestr(val):

        cls = type(val)

        if cls is str:
            val = aiomysql.escape_string(val)
        elif cls is dict:
            val = aiomysql.escape_dict(val)
        else:
            val = str(val)

        return val

    def __init__(self, client, table):

        self._client = client

        self._options = {r'table': table}


class SQLWhere():

    def __init__(self):

        pass


class _ClientBase(Utils):

    class ReadOnly(Exception):
        pass

    safestr = staticmethod(SQLQuery.safestr)

    def __init__(self, readonly=False):

        self._readonly = readonly
        self._transaction = False

    @classmethod
    def sqlwhere(cls, cond, sep=r'AND'):

        sqlstr = r''
        params = []

        if isinstance(cond, dict):

            keys = []

            for key, val in cond.items():
                keys.append(r'`{0:s}` = %s'.format(key))
                params.append(val)

            sqlstr = r' {0:s} '.format(sep.upper()).join(keys)

        else:

            sqlstr = str(cond)

        return sqlstr, params

    @property
    def readonly(self):

        return self._readonly

    @property
    def transaction(self):

        return self._transaction

    @property
    def insert_id(self):

        return None

    def _get_conn(self):

        return None

    @coroutine
    def _execute(self, sqlstr, params=None):
        self._debug(sqlstr, params)

    @coroutine
    def execute(self, sqlstr, params=None):

        cursor = yield self._execute(sqlstr, params)

        result = yield cursor.fetchall()

        return result

    def _debug(self, sqlstr, params=None):
        if params:
            sqlstr = sqlstr % tuple(r"'{0:s}'".format(self.safestr(val) if isinstance(val, str) else str(val)) for val in params)

        self.log.debug(sqlstr)

    @coroutine
    def select(self, table, what='*', where=None, having=None, order=None, group=None, limit=None, offset=None, rowlock=False):

        if rowlock and not self._transaction:
            raise self.ReadOnly()

        if self.is_iterable(what):
            what = r'`{0:s}`'.format(r'`, `'.join(what))

        params = []
        clauses = []

        if where:

            temp_str, temp_args = self.sqlwhere(where)

            clauses.append(r'WHERE {0:s}'.format(temp_str))

            if temp_args:
                params.extend(temp_args)

        if having:

            temp_str, temp_args = self.sqlwhere(having)

            clauses.append(r'HAVING {0:s}'.format(temp_str))

            if temp_args:
                params.extend(temp_args)

        if group:
            clauses.append(r'GROUP BY {0:s}'.format(group))

        if order:
            clauses.append(r'ORDER BY {0:s}'.format(order))

        if limit:
            clauses.append(r'LIMIT {0:d}'.format(limit))

        if offset:
            clauses.append(r'OFFSET {0:d}'.format(offset))

        if rowlock:
            clauses.append((r'FOR UPDATE'))

        sqlstr = r'SELECT {0:s} FROM {1:s} {2:s};'.format(
            what,
            table,
            r' '.join(clauses)
        )

        cursor = yield self._execute(sqlstr, params)

        result = yield cursor.fetchall()

        return result

    @coroutine
    def where(self, table, what='*', having=None, order=None, group=None, rowlock=False, **where):

        records = yield self.select(
            table, what,
            where[r'where'] if r'where' in where else where,
            having, order, group, 1, 0, rowlock
        )

        return records[0] if records else None

    @coroutine
    def count(self, table, what='*', **where):

        record = yield self.where(table, what=r'count({0:s}) as total'.format(what), **where)

        return record[r'total'] if record else 0

    @coroutine
    def insert(self, table, **fields):

        if self._readonly:
            raise self.ReadOnly()

        keys = []
        params = []
        for key, val in fields.items():
            keys.append(r'`{0:s}`'.format(key))
            params.append(val)

        sqlstr = r'INSERT INTO {0:s} ({1:s}) VALUES ({2:s});'.format(
            table,
            r', '.join(keys),
            r', '.join([r'%s'] * len(keys))
        )

        yield self._execute(sqlstr, params)

        return self.insert_id

    @coroutine
    def duplicate_insert(self, table, fields1, fields2):

        if self._readonly:
            raise self.ReadOnly()

        keys1 = []
        keys2 = []
        params = []

        for key, val in fields1.items():
            keys1.append(r'`{0:s}`'.format(key))
            params.append(val)

        for key, val in fields2.items():
            keys2.append(r'`{0:s}` = %s'.format(key))
            params.append(val)

        sqlstr = r'INSERT INTO {0:s} ({1:s}) VALUES ({2:s}) ON DUPLICATE KEY UPDATE {3:s};'.format(
            table,
            r', '.join(keys1),
            r', '.join([r'%s'] * len(keys1)),
            r', '.join(keys2),
        )

        yield self._execute(sqlstr, params)

        return self.insert_id

    @coroutine
    def multiple_insert(self, table, fields):

        if self._readonly:
            raise self.ReadOnly()

        sqlstr_list = []

        params = []

        for items in fields:

            keys = []

            for key, val in items.items():
                keys.append(r'`{0:s}`'.format(key))
                params.append(val)

            sqlstr = r'INSERT INTO {0:s} ({1:s}) VALUES ({2:s});'.format(
                table,
                r', '.join(keys),
                r', '.join([r'%s'] * len(keys))
            )

            sqlstr_list.append(sqlstr)

        yield self._execute('\n'.join(sqlstr_list), params)

        return self.insert_id

    @coroutine
    def update(self, tables, where, **fields):

        if self._readonly:
            raise self.ReadOnly()

        keys = []
        params = []

        for key, val in fields.items():
            keys.append(r'`{0:s}` = %s'.format(key))
            params.append(val)

        where_str, where_args = self.sqlwhere(where)
        if where_args:
            params.extend(where_args)

        sqlstr = r'UPDATE {0:s} SET {1:s} WHERE {2:s};'.format(
            tables,
            r', '.join(keys),
            where_str
        )

        cursor = yield self._execute(sqlstr, params)

        return cursor.rowcount

    @coroutine
    def increase_update(self, tables, where, fields1, fields2=None):

        if self._readonly:
            raise self.ReadOnly()

        keys = []
        params = []

        for key, val in fields1.items():
            keys.append(r'{key} = {key} + {val}'.format(key=key, val=val))
        if fields2:
            for key, val in fields2.items():
                keys.append(r'{key} = {key} + {val}'.format(key=key, val=val))

        where_str, where_args = self.sqlwhere(where)
        if where_args:
            params.extend(where_args)

        sqlstr = r'UPDATE {0:s} SET {1:s} WHERE {2:s};'.format(
            tables,
            r', '.join(keys),
            where_str
        )

        cursor = yield self._execute(sqlstr, params)

        return cursor.rowcount

    @coroutine
    def delete(self, table, where, using=None):

        if self._readonly:
            raise self.ReadOnly()

        params = []
        clauses = []

        where_str, where_args = self.sqlwhere(where)
        if where_args:
            params.extend(where_args)

        if using:
            clauses.append(r'USING {0:s}'.format(using))

        clauses.append(r'WHERE {0:s}'.format(where_str))

        sqlstr = r'DELETE FROM {0:s} {1:s};'.format(
            table,
            r' '.join(clauses)
        )

        cursor = yield self._execute(sqlstr, params)

        return cursor.rowcount


class DBClient(_ClientBase):

    def __init__(self, pool, readonly):

        super().__init__(readonly)

        self._incoming = False

        self._pool = pool
        self._conn = None

    def __del__(self):

        self.release()

    @property
    def insert_id(self):

        return self._conn.insert_id() if self._conn else 0

    @coroutine
    def _get_conn(self):

        if not self._conn and self._pool:
            self._conn = yield self._pool.acquire()

        return self._conn

    def release(self, discard=False):

        if self._conn and self._pool:

            if discard:
                self._conn.close()
                self.log.critical(r'MySQL connection destroyed')
            elif self._incoming:
                self._conn.close()
                self.log.critical(r'MySQL connection waiting for incoming data')

            self._pool.release(self._conn)
            self._conn = None

    @coroutine
    def _execute(self, sqlstr, params=None):

        if not params:
            params = None

        self._debug(sqlstr, params)

        result = None

        try:

            self._incoming = True

            conn = yield self._get_conn()

            cursor = yield conn.cursor()

            yield cursor.execute(sqlstr, params)
            yield cursor.close()

            result = cursor

        except Exception as err:

            self.release(True)

            self.log.exception(err)

            raise err

        finally:

            self._incoming = False

        return result


class DBTransaction(DBClient):

    def __init__(self, pool):

        super().__init__(pool, False)

        self._transaction = True

    def __enter__(self):

        return self

    def __exit__(self, *args):

        self.rollback()

        if(isinstance(args[1], Ignore)):

            return True

        elif(args[1]):

            return True

    def __del__(self):

        self.rollback()

    @coroutine
    def _get_conn(self):

        if(not self._conn and self._pool):
            self._conn = yield self._pool.acquire()
            yield self._conn.begin()

        return self._conn

    @coroutine
    def _execute(self, sqlstr, params=None):

        if(not params):
            params = None

        self._debug(sqlstr, params)

        result = None

        try:

            self._incoming = True

            conn = yield self._get_conn()

            cursor = yield conn.cursor()

            yield cursor.execute(sqlstr, params)
            yield cursor.close()

            result = cursor

        except Exception as err:

            self.release(True)

            self.log.exception(err)

            raise err

        finally:

            self._incoming = False

        return result

    @coroutine
    def commit(self):

        if(self._pool and self._conn):

            yield self._conn.commit()

            self._pool.release(self._conn)

            self._pool = self._conn = None

    @coroutine
    def rollback(self):

        if(self._pool and self._conn):

            yield self._conn.rollback()

            self._pool.release(self._conn)

            self._pool = self._conn = None

    def Break(self, msg=None):

        raise Ignore(msg)


safestr = SQLQuery.safestr
