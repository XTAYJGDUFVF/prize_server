

class WxConfig(object):
    """
    微信开发--基础配置

    """
    AppID = 'wx88f21215dc62ad35'  # AppID(应用ID)
    AppSecret = '61f516a6dbf2bccc21d94da255e57eb0'  # AppSecret(应用密钥)

    """微信网页开发域名"""
    AppHost = 'http://18j750y175.iask.in/weixin_auth'

    '''获取access_token'''
    config_get_access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (AppID, AppSecret)

    '''自定义菜单创建接口'''
    menu_create_url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token='

    '''自定义菜单查询接口'''
    menu_get_url = 'https://api.weixin.qq.com/cgi-bin/menu/get?access_token='

    '''自定义菜单删除接口'''
    menu_delete_url = 'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token='

    '''获取用户的UnionID'''
    get_union_id_url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN'

    '''微信公众号菜单映射数据'''
    """重定向后会带上state参数，开发者可以填写a-zA-Z0-9的参数值，最多128字节"""
    wx_menu_state_map = {
        'menuIndex0': '%s/get_card' % AppHost,  # 测试菜单1
    }

    '''关注后自动回复的消息'''
    follow_auto_reply = '欢迎关注！！！首次关注即可领取房卡5张！请回复领取！'

    '''关注领取房卡的张数'''
    focus_card_num = 5

    '''验证所需要的token'''
    token = 'test123456'

    draw_card = 'draw_card'

