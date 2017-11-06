# coding=utf-8

from util.web import RequestBaseHandlerABC
from config import Config


class RequestBaseHandler(RequestBaseHandlerABC):

    def set_default_headers(self):

        self.set_header(r'Cache-Control', r'no-cache')

        self.set_header(r'Timestamp', self.timestamp())

        origin = self.get_header(r'Origin')

        from tornado.log import app_log

        app_log.info(r'{} {} {}'.format(origin, self.request.method, Config.Debug))

        if(origin):

            if(Config.Debug):

                self.set_header(r'Access-Control-Allow-Origin', r'*')

            else:

                allow_origin = Config.AccessControlAllowOrigin

                if(r'*' in allow_origin or origin in allow_origin):
                    self.set_header(r'Access-Control-Allow-Origin', origin)

            method = self.get_header(r'Access-Control-Request-Method')
            if(method):
                self.set_header(r'Access-Control-Allow-Methods', method)

            headers = self.get_header(r'Access-Control-Request-Headers')
            if(headers):
                self.set_header(r'Access-Control-Allow-Headers', headers)

            self.set_header(r'Access-Control-Max-Age', r'86400')
            self.set_header(r'Access-Control-Allow-Credentials', r'true')
