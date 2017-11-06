from weixinback.core.logger_helper import logger
from tornado.gen import coroutine
from util.decorator import catch_error
from model.base import BaseModel


class TokenCache(BaseModel):
    """
    微信token缓存

    set_cache               添加redis
    get_cache               获取redis
    """
    _expire_access_token = 7000   # 微信access_token过期时间, 2小时,安全起见设置为此
    KEY_ACCESS_TOKEN = 'access_token'  # 微信全局唯一票据access_token

    @coroutine
    def set_access_cache(self, key, value):
        """添加微信access_token验证相关redis"""
        with catch_error():
            cache_client = self.get_cache_client()
            res = yield cache_client.set(key, value, expire=self._expire_access_token)
            if not res:
                return None
        return True

    @coroutine
    def get_access_cache(self, key):
        """获取redis"""
        with catch_error():
            cache_client = self.get_cache_client()
            res = yield cache_client.get(key)
            if not res:
                return None
        return res

