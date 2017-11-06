# coding=utf-8

from tornado.gen import coroutine
from util.decorator import catch_error
from config import Config
from .base import BaseModel
from .m_error import ErrorCode
from util.util import Utils



class DrawCardInfo(BaseModel):

    @coroutine
    def initial_draw_card_info(self, account_info):
        """
        插入本地创建的领取记录表,并且对房卡进行增加
        :param account_info:
        :return:
        """
        result = False
        with catch_error():
            insert_map = {}
            insert_map['user_id'] = account_info['UserID']
            insert_map['union_id'] = account_info['unionid']
            insert_map['create_time'] = Utils.timestamp()
            db_client = self.get_db_client()
            res_insert_draw = yield db_client.insert('draw_card_info', **insert_map)
            if res_insert_draw < 0:
                self.Break()
            uid = account_info['UserID']
            '''本地数据库试验'''
            # res_insert_score = yield db_client.increase_update(r'game_score_info', where={'user_id': uid},
            #                                                    fields1={'insure_score': 5})
            # if not res_insert_score > 0:
            #     self.Break()

            '''mssql数据库正式操作'''
            # mssql_score_conn = self.get_mssql_conn(Config.MssqlTreasureDbName)
            # with mssql_score_conn.cursor() as cur:
            #     cur.execute(r"update GameScoreInfo set InsureScore = InsureScore + {} where UserID = {}".format(
            #                                                                                             5,
            #                                                                                             uid))
            #     rowcount = cur.rowcount
            #     if not rowcount > 0:
            #         self.Break()
            # mssql_score_conn.commit()
            # mssql_score_conn.close()
            result = True
        return result

    @coroutine
    def search_card_info(self, union_id):
        """
        从本地的领取记录表中查找是否有该用户信息
        :param union_id:
        :return:
        """
        result = False
        with catch_error():
            db_client = self.get_db_client()
            res = yield db_client.select('draw_card_info', what='union_id', where={'union_id': union_id})
            print(res)
            if not res:
                self.Break()
            result = True
        return result



