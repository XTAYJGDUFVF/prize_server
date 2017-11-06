import random
from tornado.gen import coroutine
from tornado.log import app_log

from util.decorator import catch_error
from config import Config
from .m_error import ErrorCode
from .base import BaseModel
from util.util import Utils


class AccountInfo(BaseModel):



    @coroutine
    def get_mssql_user_info_by_union_id(self, union_id):
        '''
        微信用，从sql Server中查找该用户是否存在
        不存在的话让其注册关联，返回None
        1、存在的话返回相应的用户信息 Accounts, NickName
        2、写到mysql数据库的weixin_account_draw
        3、返回NickName
        '''
        result = [False, ErrorCode.Unknown]
        with catch_error():
            mssql_account_conn = self.get_mssql_conn(Config.MssqlAccountDbName)
            with mssql_account_conn.cursor() as cur:
                cur.execute(r"select top 1 UserID, unionid from AccountsInfo where unionid = '{}'".format(union_id,))
                _infos = cur.fetchall()
            mssql_account_conn.close()
            if not _infos:
                result[1] = ErrorCode.AccountNotFound.set_extra(r'account not found')
                self.Break()
            result[0] = True
            result[1] = _infos[0]
        return result


    @coroutine
    def get_mssql_user_info_by_user_id(self, user_id):
        '''
        抽奖活动用，用来获取数据，添加到本地的mysql数据库中作为关联
        :param user_id:
        :return:
        '''
        result = [False, ErrorCode.Unknown]
        with catch_error():
            mssql_account_conn = self.get_mssql_conn(Config.MssqlAccountDbName)
            with mssql_account_conn.cursor() as cur:
                cur.execute(r"select top 1 UserID,NickName from AccountsInfo where UserID = {}".format(user_id))
                _infos = cur.fetchall()
            mssql_account_conn.close()
            if not _infos:
                result[1] = ErrorCode.AccountNotFound.set_extra(r'该用户不存在！')
                self.Break()
            result[0] = True
            result[1] = _infos
        return result
