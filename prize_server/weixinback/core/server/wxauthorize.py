from weixinback.core.logger_helper import logger
import hashlib
import time
from weixinback.core.server import wxshedule
from weixinback.core.server import analysis_chance
from weixinback.core.server.wxconfig import WxConfig
from tornado.gen import coroutine
from controller.base import RequestBaseHandler
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

func_dict = {
    WxConfig.draw_card: analysis_chance.AnalysisChance().get_draw_status,

}

class WxSignatureHandler(RequestBaseHandler):
    """
    微信服务器签名验证, 消息回复

    check_signature: 校验signature是否正确
    """

    def data_received(self, chunk):
        pass

    @coroutine
    def get(self):
        try:
            signature = self.get_argument('signature')
            timestamp = self.get_argument('timestamp')
            nonce = self.get_argument('nonce')
            echostr = self.get_argument('echostr')
            logger.debug('微信sign校验,signature='+signature+',&timestamp='+timestamp+'&nonce='+nonce+'&echostr='+echostr)
            result = yield self.check_signature(signature, timestamp, nonce)
            if result:
                logger.debug('微信sign校验,返回echostr='+echostr)
                wxshedule.WxShedule().excute()
                self.write(echostr)

            else:
                logger.error('微信sign校验,---校验失败')
        except Exception as e:
            logger.error('微信sign校验,---Exception' + str(e))

    @coroutine
    def post(self):
        body = self.request.body
        logger.debug('微信消息回复中心 收到用户消息' + str(body.decode('utf-8')))
        data = ET.fromstring(body)
        ToUserName = data.find('ToUserName').text
        FromUserName = data.find('FromUserName').text
        MsgType = data.find('MsgType').text
        if MsgType == 'text' or MsgType == 'voice':
            '''文本消息 or 语音消息'''
            try:
                MsgId = data.find("MsgId").text
                if MsgType == 'text':
                    Content = data.find('Content').text  # 文本消息内容
                elif MsgType == 'voice':
                    Content = data.find('Recognition').text  # 语音识别结果，UTF8编码
                if Content == u'你好':
                    reply_content = '您好,请问有什么可以帮助您的吗?'
                #分析该用户是否还有机会，返回的就是需要展示的字符串
                elif Content == u'领取':
                    reply_content = yield analysis_chance.AnalysisChance().get_draw_status(FromUserName)
                else:
                    # 查找不到关键字,默认回复
                    reply_content = "客服小儿智商不够用啦~"
                if reply_content:
                    CreateTime = int(time.time())
                    out = yield self.reply_text(FromUserName, ToUserName, CreateTime, reply_content)
                    self.write(out)
            except:
                pass

        elif MsgType == 'event':
            '''接收事件推送'''
            try:
                Event = data.find('Event').text
                if Event == 'subscribe':
                    # 关注事件
                    CreateTime = int(time.time())
                    reply_content = WxConfig.follow_auto_reply
                    out = yield self.reply_text(FromUserName, ToUserName, CreateTime, reply_content)
                    self.write(out)
                elif Event == 'CLICK':
                    # 领取时间
                    CreateTime = int(time.time())
                    EventKey = data.find('EventKey').text
                    reply_content = yield func_dict[EventKey](FromUserName)
                    out = yield self.reply_text(FromUserName, ToUserName, CreateTime, reply_content)
                    self.write(out)


            except:
                pass

    @coroutine
    def reply_text(self, FromUserName, ToUserName, CreateTime, Content):
        """回复文本消息模板"""
        textTpl = """<xml> <ToUserName><![CDATA[%s]]></ToUserName> <FromUserName><![CDATA[%s]]></FromUserName> <CreateTime>%s</CreateTime> <MsgType><![CDATA[%s]]></MsgType> <Content><![CDATA[%s]]></Content></xml>"""
        out = textTpl % (FromUserName, ToUserName, CreateTime, 'text', Content)
        return out

    @coroutine
    def check_signature(self, signature, timestamp, nonce):
        """校验token是否正确"""
        token = WxConfig.token
        L = [timestamp, nonce, token]
        L.sort()
        s = L[0] + L[1] + L[2]
        sha1 = hashlib.sha1(s.encode('utf-8')).hexdigest()
        logger.debug('sha1=' + sha1 + '&signature=' + signature)
        return sha1 == signature



