import requests
import json
from weixinback.core.server.wxconfig import WxConfig
from weixinback.core.cache.tokencache import TokenCache
from weixinback.core.logger_helper import logger
from tornado.gen import coroutine
from controller.base import RequestBaseHandler

class WxMenuServer(RequestBaseHandler):
    """
    微信自定义菜单

    create_menu                     自定义菜单创建接口
    get_menu                        自定义菜单查询接口
    delete_menu                     自定义菜单删除接口
    create_menu_data                创建菜单数据
    """

    _token_cache = TokenCache()     # 微信token缓存

    @coroutine
    def get(self):
        '''创建菜单数据'''
        # wx_menu_server.create_menu_data()
        # '''自定义菜单创建接口'''
        control = self.get_arg_str('todo')
        if control == 'create':
            yield self.create_menu()
        '''自定义菜单查询接口'''
        if control == 'search':
            yield self.get_menu()
        '''自定义菜单删除接口'''
        if control == 'delete':
            yield self.delete_menu()

    @coroutine
    def create_menu(self):

        """自定义菜单创建接口"""
        access_token = yield self._token_cache.get_access_cache(self._token_cache.KEY_ACCESS_TOKEN)
        if access_token:
            url = WxConfig.menu_create_url + access_token
            data = yield self.create_menu_data()
            r = requests.post(url, data.encode('utf-8'))
            logger.debug('【微信自定义菜单】自定义菜单创建接口Response[' + str(r.status_code) + ']')
            if r.status_code == 200:
                res = r.text
                logger.debug('【微信自定义菜单】自定义菜单创建接口' + res)
                json_res = json.loads(res)
                if 'errcode' in json_res.keys():
                    errcode = json_res['errcode']
                    return errcode
        else:
            logger.error('【微信自定义菜单】自定义菜单创建接口获取不到access_token')

    @coroutine
    def get_menu(self):
        """自定义菜单查询接口"""
        access_token = yield self._token_cache.get_access_cache(self._token_cache.KEY_ACCESS_TOKEN)
        if access_token:
            url = WxConfig.menu_get_url + access_token
            r = requests.get(url)
            logger.debug('【微信自定义菜单】自定义菜单查询接口Response[' + str(r.status_code) + ']')
            if r.status_code == 200:
                res = r.text
                logger.debug('【微信自定义菜单】自定义菜单查询接口' + res)
                json_res = json.loads(res)
                if 'errcode' in json_res.keys():
                    errcode = json_res['errcode']
                    return errcode
        else:
            logger.error('【微信自定义菜单】自定义菜单查询接口获取不到access_token')

    @coroutine
    def delete_menu(self):
        """自定义菜单删除接口"""
        access_token = yield self._token_cache.get_access_cache(self._token_cache.KEY_ACCESS_TOKEN)
        if access_token:
            url = WxConfig.menu_delete_url + access_token
            r = requests.get(url)
            logger.debug('【微信自定义菜单】自定义菜单删除接口Response[' + str(r.status_code) + ']')
            if r.status_code == 200:
                res = r.text
                logger.debug('【微信自定义菜单】自定义菜单删除接口' + res)
                json_res = json.loads(res)
                if 'errcode' in json_res.keys():
                    errcode = json_res['errcode']
                    return errcode
        else:
            logger.error('【微信自定义菜单】自定义菜单删除接口获取不到access_token')

    @coroutine
    def create_menu_data(self):
        """创建菜单数据"""
        menu_data = {'button': []}  # 大菜单
        menu_Index0 = {
            # 'type': 'view',
            # 'name': '测试菜单1',
            # 'url': WxConfig.wx_menu_state_map.get('menuIndex0')
            'type': 'click',
            'name': '领取',
            'key': 'draw_card',
        }
        menu_data['button'].append(menu_Index0)
        MENU_DATA = json.dumps(menu_data, ensure_ascii=False)
        logger.debug('【微信自定义菜单】创建菜单数据MENU_DATA[' + str(MENU_DATA) + ']')
        return MENU_DATA

