# coding=utf-8

from tornado.gen import coroutine
from util.decorator import catch_error
from config import Config
from .base import BaseModel
from .m_error import ErrorCode
from util.util import Utils


class CardUsedInfoModel(BaseModel):

    @coroutine
    def today_used_info(self, uid):
        result = [False, ErrorCode.NotFoundUser]

        with catch_error():
            mssql_account_conn = self.get_mssql_conn(Config.MssqlRecordDbName)
            today_zero = Utils.today_zero()
            # today_zero = 0
            # uid = 5658      # 42
            with mssql_account_conn.cursor() as cur:
                cur.execute(r"""select 
                                sum(CostValue) as today_used_count 
                                from RecordPrivateCost 
                                where UserID={0}
                                and DATEDIFF(s, '1970-01-01 00:00:00', CostDate) > {1}
                                and CostFrom in (1,2)""".format(uid, today_zero))
                _infos = cur.fetchall()
            mssql_account_conn.close()
            # print(_infos)
            if not _infos[0]['today_used_count']:
                return result
            if _infos[0]['today_used_count'] > 0:
                result[0] = True
                result[1] = _infos
            if _infos[0]['today_used_count'] < 0:
                return result
        return result

