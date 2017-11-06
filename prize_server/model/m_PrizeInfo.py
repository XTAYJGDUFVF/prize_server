# coding=utf-8

from tornado.gen import coroutine
from util.decorator import catch_error
from .base import BaseModel
from .m_error import ErrorCode
from config import Config





class PrizeInfoModel(BaseModel):

    @coroutine
    def init_prize_info(self):
        result = [False, ErrorCode.Unknown]
        with catch_error():
            db_client = self.get_db_client()
            prize_info = yield db_client.select(r'prize_info', what='*', where={'prize_status': 1})
            if not prize_info:
                result[1] = ErrorCode.Search.set_extra("获取奖品信息失败")
                self.Break()
            result[0] = True
            result[1] = prize_info
        return result


    @coroutine
    def get_prize_info(self):
        result = [False, ErrorCode.Unknown]
        with catch_error():
            cache_client = self.get_cache_client()  # 先从缓存中获取
            prize_list = yield cache_client.get("prize_list")
            if prize_list:
                result[0] = True
                result[1] = prize_list
                return result
            else:
                prize_info = yield self.init_prize_info()    # 没有的话初始化一下
                if not prize_info[0]:
                    result[1] = prize_info[1]
                    self.Break()
            prize_list, prize_need_list = yield self.deal_info(prize_info[1])       # 处理奖品的数据结构
            set_prize_list_status = yield cache_client.set("prize_list", prize_list, expire=Config.RedisExpires)
            set_prize_need_list_status = yield cache_client.set("prize_need_list", prize_need_list, expire=Config.RedisExpires)
            if not set_prize_list_status or not set_prize_need_list_status:
                result[1] = ErrorCode.Redis.set_extra('设置缓存失败')
            else:
                result[0] = True
                result[1] = prize_list
        return result

    @coroutine
    def deal_info(self, prize_info):
        prize_list = []
        prize_need_list = []
        for per in prize_info:
            prize_list.append({per['prize_id']: per['picture_url']})
            prize_need_list.append({per['prize_id']: {'probability': per['prize_probability'],
                                                      'prize_num': per['prize_num'],
                                                      'largest_perday': per['largest_num_everyday'],
                                                      'largest_per_get': per['largest_per_person_get'],
                                                      'prize_control': per['prize_control']}})
        return prize_list, prize_need_list

    @coroutine
    def get_need_list_info(self):
        result = None
        cache_client = self.get_cache_client()
        prize_need_list = yield cache_client.get("prize_need_list")
        if prize_need_list:
            pass
            return prize_need_list
        else:
            prize_info = yield self.init_prize_info()
        if not prize_info[0]:
            return prize_info
        prize_list, prize_need_list = yield self.deal_info(prize_info[1])
        yield cache_client.set("prize_info", prize_list, expire=Config.RedisExpires)
        yield cache_client.set("prize_need_list", prize_need_list, expire=Config.RedisExpires)
        if prize_need_list:
            result = prize_need_list
        return result
