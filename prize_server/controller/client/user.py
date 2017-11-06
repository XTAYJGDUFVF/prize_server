# coding=utf8

from tornado.gen import coroutine

from model.m_AccountInfo import AccountInfo
from model.m_MakePrize import MakePrize
from model.m_PrizeLog import PrizeLog
from model.m_PrizeInfo import PrizeInfoModel
from model.m_CardUsedInfo import CardUsedInfoModel
from model.m_test import Tests

from util.prize_id import Prize_Id
from model.m_error import ErrorCode
from ..base import RequestBaseHandler


class InitialInfo(RequestBaseHandler):
    """
    点击页面初始化的时候，
    1、菜单基本信息，从redis中获取或从mysql中获取
    2、剩余抽奖次数，从数据库获取
    """
    @coroutine
    def get(self):
        uid = self.get_arg_int(r'uid')
        '''用奖品信息模块  抽奖模块'''
        m_prizeinfo = PrizeInfoModel()
        m_makeprize = MakePrize()

        prize_info = yield m_prizeinfo.get_prize_info()     # 获取获奖信息
        initial_chance = yield m_makeprize.initial_chance_info(uid)  # 初始化用户信息并且拿到用户剩余抽奖次数
        if not prize_info[0]:
            error_code = prize_info[1]
            print(error_code)
            return self.write_json(ErrorCode.get_error_response(error_code), 400)
        if not initial_chance[0]:
            error_code = initial_chance[1]
            return self.write_json(ErrorCode.get_error_response(error_code), 400)
        return self.write_json({r'left_chance': initial_chance[1], r'prize_info': prize_info}, 200)


class GetPrize(RequestBaseHandler):

    @coroutine
    def get(self):
        uid = self.get_arg_int(r'uid')
        m_make_prize = MakePrize()
        m_prize_info = PrizeInfoModel()
        prize_need_list = yield m_prize_info.get_need_list_info()
        if not prize_need_list:
            error_code = ErrorCode.NeedListNotFound.set_extra(r'need prize list not found')
            return self.write_json(ErrorCode.get_error_response(error_code), 500)
        '''看剩余次数，有没有机会领取'''
        left_chance = yield m_make_prize.get_left_chance(uid)
        if not left_chance:
            return self.write_json({'prize_id': -1, 'left_chance': 0}, 200)
        '''有机会的话，生成奖品ID'''
        prize_id = yield self.get_prize_id(uid, prize_need_list)
        plus_num = prize_need_list[prize_id - 1][prize_id]['prize_control']
        '''开始记录'''
        m_prize_log = PrizeLog()
        res = yield m_prize_log.write_log(uid, prize_id, plus_num)
        if not res[0]:
            return self.write_json(ErrorCode.get_error_response(res[1]), 500)
        return self.write_json({'prize_id': prize_id, 'left_chance': left_chance - 1}, 200)

    @coroutine
    def get_prize_id(self, uid, prize_need_list):
        prize_id = yield Prize_Id(prize_need_list).get_id()
        if prize_need_list[prize_id - 1][prize_id]['prize_num'] == None:
            return prize_id
        m_prize_log = PrizeLog()
        per_today_prize_count = yield m_prize_log.per_today_prize_count(uid, prize_id)  # 今天该人获得的总数
        all_today_prize_count = yield m_prize_log.all_today_prize_count(prize_id)       # 今天该奖项获得的总数
        largest_perday = prize_need_list[prize_id - 1][prize_id]['largest_perday']      # 该奖项获得最大数
        largest_per_get = prize_need_list[prize_id - 1][prize_id]['largest_per_get']    # 单人获得最大数
        if all_today_prize_count < largest_per_get and per_today_prize_count < largest_perday:
            return prize_id
        if all_today_prize_count >= largest_per_get or per_today_prize_count >= largest_perday:
            yield self.get_prize_id(uid)


class ReadLog(RequestBaseHandler):

    @coroutine
    def get(self):
        uid = self.get_arg_int(r'uid')
        m_prize_log = PrizeLog()
        prize_log = yield m_prize_log.read_log(uid)
        if not prize_log:
            return self.write_json({'prize_log': None}, 400)

        return self.write_json({'prize_log': prize_log}, 200)


class Test(RequestBaseHandler):

    @coroutine
    def get(self):
        m_test = Tests().test()
