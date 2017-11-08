from util.util import Singleton
from tornado.gen import coroutine
from weixinback.core.server.wxconfig import WxConfig
from ..cache.tokencache import TokenCache
import requests
import json
from model import m_AccountInfo
from model import m_DrawCardInfo

class AnalysisChance(Singleton):
    '''
    分析该用户是否有机会领取奖励
    0、是否有下载游戏注册账号
    1、有机会就返回领取成功的字符串
    2、没有机会的话返回没有机会的字符串
    '''
    _token_cache = TokenCache()  # 微信token缓存


    @coroutine
    def get_union_id(self, open_id):
        """
        根据open_id获取union_id
        :param open_id:
        :return:
        """
        access_token = yield self._token_cache.get_access_cache(self._token_cache.KEY_ACCESS_TOKEN)
        union_id_url = WxConfig.get_union_id_url.format(ACCESS_TOKEN=access_token,
                                                        OPENID=open_id)
        request_union_id = requests.get(union_id_url)
        res_info = json.loads(request_union_id.text, encoding='utf-8')
        union_id = res_info.get('unionid')
        nickname = res_info.get('nickname')
        return union_id, nickname

    @coroutine
    def get_draw_status(self, open_id):
        """
        根据open_id返回需要返回的字符串
        :param open_id:
        :return:
        """
        union_id, nickname = yield self.get_union_id(open_id)
        m_account_info = m_AccountInfo.AccountInfo()
        m_draw_card_info = m_DrawCardInfo.DrawCardInfo()
        draw_card_info = yield m_draw_card_info.search_card_info(union_id)
        if draw_card_info:
            return '%s,你已经领取过了！' % (nickname,)
        else:
            union_id_info = yield m_account_info.get_mssql_user_info_by_union_id(union_id)      # 返回一个字典
            if union_id_info[0]:
                initial_draw_status = yield m_draw_card_info.initial_draw_card_info(union_id_info[1])
                if initial_draw_status:
                    return '%s,领取成功，快去游戏吧！' % (nickname,)
            return '%s,您没有登录绑定游戏，快去下载绑定吧！' % (nickname,)
