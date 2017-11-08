# coding=utf-8

from tornado.gen import coroutine
from util.decorator import catch_error
from .base import BaseModel
from util.util import Utils
from .m_error import ErrorCode
from config import Config

class PrizeLog(BaseModel):

    @coroutine
    def write_log(self, uid, prize_id, plus_num):
        result = [False, ErrorCode.Unknown]
        param = {
            'user_id': uid,
            'create_time': Utils.timestamp(),
            'prize_id': prize_id
        }

        with catch_error():
            db_client = self.get_db_client()
            if plus_num:                # 插入获奖日志，并且增加房卡
                if plus_num > 0:        # 需要增加房卡的

                    '''本地试验增加房卡'''
                    # update_score_statu = yield db_client.increase_update(r'game_score_info',
                    #                                                      where={'user_id': uid},
                    #                                                      fields1={'insure_score': plus_num})
                    # # print(2, update_score_statu, prize_id, plus_num)    # 0
                    # if update_score_statu < 0:
                    #     result[1] = ErrorCode.Database.set_extra('增加房卡失败！')
                    #     self.Break()

                    '''上线数据库增加房卡'''
                    mssql_score_conn = self.get_mssql_conn(Config.MssqlTreasureDbName)
                    with mssql_score_conn.cursor() as cur:
                        cur.execute(r"""update GameScoreInfo set InsureScore =
                                        InsureScore + {} where UserID = {}""".format(plus_num, uid))
                        rowcount = cur.rowcount
                        if not rowcount > 0:
                            result[1] = ErrorCode.Database.set_extra(r'添加房卡失败！')
                            self.Break()
                    mssql_score_conn.commit()
                    mssql_score_conn.close()

                '''更新获奖日志，需要加京东卡或红包的'''
                insert_statu = yield db_client.insert('prize_log', **param)
                # print(1, insert_statu)  # 0
                if insert_statu < 0:
                    result[1] = ErrorCode.Database.set_extra('插入日志失败！')
                    self.Break()


            '''更新领奖次数'''
            update_statu = yield db_client.increase_update('make_prize',
                                                           where={'user_id': uid},
                                                           fields1={'left_chance': -1},
                                                           fields2={'used_chance': 1})
            # print(3, update_statu)  # 1
            if not update_statu > 0:
                result[1] = ErrorCode.Database.set_extra('更新领取表失败！')
                self.Break()


            result[0] = True
        return result

    @coroutine
    def per_today_prize_count(self, uid, prize_id):     # 该奖项今天该人获得的数量
        num = None
        with catch_error():
            db_client = self.get_db_client()
            today_zero = Utils.today_zero()
            sql_where = 'user_id = %s and prize_id = %s and create_time > %d' % (uid, prize_id, today_zero)
            res = yield db_client.select(r'prize_log', what='count(1) as per_today_prize_count', where=sql_where)
            if res:
                num = res[0]['per_today_prize_count']
        return num

    @coroutine
    def all_today_prize_count(self, prize_id):
        num = None
        with catch_error():
            db_client = self.get_db_client()
            today_zero = Utils.today_zero()
            sql_where = 'prize_id = %s and create_time > %d' % (prize_id, today_zero)
            res = yield db_client.select(r'prize_log', what='count(1) as all_today_prize_count', where=sql_where)
            if res:
                num = res[0]['all_today_prize_count']
        return num

    @coroutine
    def read_log(self, uid):
        result = None
        with catch_error():
            db_client = self.get_db_client()
            result = yield db_client.select('prize_log left join prize_info on prize_log.prize_id = prize_info.prize_id',
                                            what="FROM_UNIXTIME(create_time, '%%Y-%%m-%%d %%H:%%i:%%S') as date_info, prize_info.prize_name",
                                            where={'user_id': uid}, order='create_time desc', limit=5)
            if not result:
                return False
        return result
