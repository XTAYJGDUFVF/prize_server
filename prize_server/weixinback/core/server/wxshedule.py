from weixinback.core.logger_helper import logger
import tornado.ioloop
import requests
import json
from weixinback.core.server.wxconfig import WxConfig
from weixinback.core.cache.tokencache import TokenCache
from tornado.gen import coroutine

class WxShedule(object):
    """
    定时任务调度器

    excute                      执行定时器任务
    get_access_token            获取微信全局唯一票据access_token
    get_jsapi_ticket           获取JS_SDK权限签名的jsapi_ticket
    """
    _token_cache = TokenCache()  # 微信token缓存实例
    _expire_time_access_token = 7000 * 1000  # token过期时间

    def excute(self):
        """执行定时器任务"""
        logger.info('【获取微信全局唯一票据access_token】>>>执行定时器任务')
        tornado.ioloop.IOLoop.instance().call_later(0, self.get_access_token)
        tornado.ioloop.PeriodicCallback(self.get_access_token, self._expire_time_access_token).start()

    @coroutine
    def get_access_token(self):
        """获取微信全局唯一票据access_token"""
        url = WxConfig.config_get_access_token_url
        r = requests.get(url)
        if r.status_code == 200:
            res = r.text
            d = json.loads(res)
            if 'access_token' in d.keys():
                access_token = d['access_token']
                # 添加至redis中
                yield self._token_cache.set_access_cache(self._token_cache.KEY_ACCESS_TOKEN, access_token)
            elif 'errcode' in d.keys():
                errcode = d['errcode']
                tornado.ioloop.IOLoop.instance().call_later(10, self.get_access_token)
        else:
            logger.error('【获取微信全局唯一票据access_token】request access_token error, will retry get_access_token() method after 10s')
            tornado.ioloop.IOLoop.instance().call_later(10, self.get_access_token)

