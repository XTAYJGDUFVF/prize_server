# coding=utf-8


from controller import client
from weixinback.core.server import wxauthorize
from weixinback.core.server import wxmenu

urls = [


    (r'/initial_info/?',                                                client.user.InitialInfo),
    (r'/get_prize/?',                                                   client.user.GetPrize),
    (r'/prize_log/?',                                                   client.user.ReadLog),

    (r'/weixin_auth',                                                   wxauthorize.WxSignatureHandler),
    (r'/control_menu/?',                                                wxmenu.WxMenuServer),


]
