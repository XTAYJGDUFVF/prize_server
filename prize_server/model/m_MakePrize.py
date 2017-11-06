# coding=utf-8

from tornado.gen import coroutine
from util.decorator import catch_error
from config import Config
from .base import BaseModel
from .m_error import ErrorCode
from .m_CardUsedInfo import CardUsedInfoModel
from .m_AccountInfo import AccountInfo

from util.util import Utils


class MakePrize(BaseModel):


    @coroutine
    def initial_chance_info(self, uid):
        result = [False, ErrorCode.Unknown]
        with catch_error():
            db_client = self.get_db_client()
            info = yield db_client.select(r'make_prize',
                                          what='first_time,left_chance,used_chance',
                                          where={'user_id': uid})  # 查找本地账户是否有该人
            total_chance = Config.TotalChance           # 如果有的话，拿到该人的最后一次领取时间
            # print(1, info)          # [{'first_time': 150993117, 'left_chance': 0, 'used_chance': 1}]
            if info:
                first_time = info[0]['first_time']
            if not info:                                # 如果没有的话，初始化本地该人账户
                '''先从sqlserver中查找该人信息'''
                m_account_info = AccountInfo()          # 从账户中查找该人信息
                user_info = yield m_account_info.get_mssql_user_info_by_user_id(uid)
                # print(2, user_info)     # [True, [{'UserID': 120, 'NickName': '游客7486118'}]]
                if user_info[0]:                     # 如果有该用户的话，写入本地账户
                    insert_map = {}
                    insert_map['create_time'] = Utils.timestamp()
                    insert_map['user_id'] = user_info[1][0]['UserID']
                    insert_map['nick_name'] = user_info[1][0]['NickName']
                    insert_account_statu = yield db_client.insert('account_info',
                                                                  **insert_map)
                    # print(3, insert_account_statu)      # 120
                    if insert_account_statu < 0:               # 如果没有插入成功的话
                        result[1] = ErrorCode.Database.set_extra(r'初始化时插入用户表中信息失败！')
                        self.Break()
                    else:                                       #插入成功的话，再往make_prize中插
                        param = {
                            'user_id': uid,
                            'first_time': Utils.timestamp(),
                            'left_chance': 1,
                            'used_chance': 0,
                            'added_chance': 1,
                        }
                        insert_make_prize_statu = yield db_client.insert('make_prize',
                                                                         **param)
                        # print(4, insert_make_prize_statu)   # 0
                        if insert_make_prize_statu < 0:     # 成功的话返回None
                            result[1] = ErrorCode.Database.set_extra(r'插入本地奖品次数表失败！')
                            self.Break()
                        first_time = param['first_time']
                else:                               # 没有该用户信息的话
                    result[1] = user_info[1]
                    self.Break()
            if first_time < Utils.today_zero():     # 如果领取时间是昨天，就刷领取信息
                param = {
                    'first_time': Utils.timestamp(),
                    'left_chance': 1,
                    'used_chance': 0,
                    'added_chance': 1,
                }
                flush_status = yield db_client.update('make_prize',
                                                      **param,
                                                      where={'user_id': uid})
                # print(5, flush_status)      # 1
                if flush_status < 0:                # 成功的话返回1， row_count
                    result[1] = ErrorCode.Database.set_extra(r'刷新用户信息失败！')
                    self.Break()
            info = yield db_client.select(r'make_prize',
                                          what='left_chance,used_chance,added_chance',
                                          where={'user_id': uid})
            # print(6, info)      # [{'left_chance': 1, 'used_chance': 0, 'added_chance': 1}]
            left_chance = info[0]['left_chance']
            added_chance = info[0]['added_chance']
            today_used_count = yield CardUsedInfoModel().today_used_info(uid)
            # print(7, today_used_count)      # [False, -20017 ]
            if not today_used_count[0]:
                today_used = 0
            if today_used_count[0]:
                today_used = today_used_count[1][0]['today_used_count']
                if today_used <= 0:
                    today_used = 0
            all_time = divmod(today_used, Config.EveryChanceRequire)[0]
            all_times = all_time if all_time < total_chance else total_chance
            add_time = all_times - added_chance
            if add_time < 0:
                add_time = 0
            add_time_status = yield db_client.increase_update(r'make_prize',
                                                              where={'user_id': uid},
                                                              fields1={'left_chance': add_time},
                                                              fields2={'added_chance': add_time})
            # print(8, add_time_status)   # 0
            if add_time_status < 0:     # 受影响的行数  0
                result[1] = ErrorCode.Database.set_extra("更新奖品次数失败！")
                self.Break()
            result[1] = left_chance + add_time
            result[0] = True
        return result

    @coroutine
    def get_left_chance(self, uid):
        with catch_error():
            db_client = self.get_db_client()
            res = yield db_client.select('make_prize',
                                         what='left_chance',
                                         where={'user_id': uid})
            if res:
                if res[0]['left_chance'] <= 0:
                    return False
                res = res[0]['left_chance']
        return res








