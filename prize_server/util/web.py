# coding=utf-8

from tornado.concurrent import Future
from tornado.gen import coroutine
from tornado.web import RequestHandler

from .struct import ErrorData, Ignore
from .util import Utils


class RequestBaseHandlerABC(RequestHandler, Utils):

    def __init__(self, application, request, **kwargs):

        self._prepare = []
        self._on_finish = []

        self._payload = kwargs

        RequestHandler.__init__(self, application, request)

    def head(self, *args, **kwargs):

        self.finish()

    def options(self, *args, **kwargs):

        self.finish()

    @coroutine
    def prepare(self):

        self._parse_json_arguments()

        if self._prepare:
            for func in self._prepare:
                result = func()
                if isinstance(result, Future):
                    yield result

    def on_finish(self):

        if self._on_finish:
            for func in self._on_finish:
                func()

    def set_default_headers(self):

        pass

    def set_cookie(self, name, value, domain=None, expires=None, path="/", expires_days=None, **kwargs):

        if type(value) not in (str, bytes):
            value = str(value)

        return super().set_cookie(name, value, domain, expires, path, expires_days, **kwargs)

    def set_secure_cookie(self, name, value, expires_days=30, version=None, **kwargs):

        if type(value) not in (str, bytes):
            value = str(value)

        return super().set_secure_cookie(name, value, expires_days, version, **kwargs)

    def compute_etag(self):

        return None

    def _parse_json_arguments(self):

        self.request.json_arguments = {}

        content_type = self.content_type

        if content_type and content_type.find(r'application/json') >= 0 and self.body:

            try:

                json_args = self.json_decode(self.body)

                if isinstance(json_args, dict):

                    self.request.json_arguments.update(json_args)

                    for key, val in self.request.json_arguments.items():

                        if not isinstance(val, str):
                            val = str(val)

                        self.request.arguments.setdefault(key, []).append(val)

            except:

                self.log.debug(r'Invalid application/json body: {0}'.format(self.body))

    @property
    def request_module(self):

        return r'{0}.{1}'.format(self.module, self.method)

    @property
    def module(self):

        return r'{0}.{1}'.format(self.__class__.__module__, self.__class__.__name__)

    @property
    def method(self):

        return self.request.method.lower()

    @property
    def version(self):

        return self.request.version.lower()

    @property
    def protocol(self):

        return self.request.protocol

    @property
    def host(self):

        return self.request.host

    @property
    def path(self):

        return self.request.path

    @property
    def query(self):

        return self.request.query

    @property
    def body(self):

        return self.request.body

    @property
    def files(self):

        return self.request.files

    @property
    def referer(self):

        return self.get_header(r'Referer', r'')

    @property
    def client_ip(self):

        return self.get_header(r'X-Real-IP', self.request.remote_ip)

    @property
    def content_type(self):

        return self.get_header(r'Content-Type', r'')

    @property
    def content_length(self):

        result = self.get_header(r'Content-Length', r'')

        return int(result) if result.isdigit() else 0

    def get_header(self, name, default=None):
        """
        获取header数据
        """
        return self.request.headers.get(name, default)

    def get_files(self, name):
        """
        获取files数据
        """
        result = []

        file_data = self.files.get(name, None)

        if file_data is not None:
            self.list_extend(result, file_data)

        for index in range(len(self.files)):

            file_data = self.files.get(r'{0:s}[{1:d}]'.format(name, index), None)

            if file_data is not None:
                self.list_extend(result, file_data)

        return result

    def get_arg_str(self, name, default=r'', length=0, sqlsafe=False):
        """
        获取str型输入
        """
        result = self.get_argument(name, None, True)

        if result is None:
            return default

        if not isinstance(result, str):
            result = str(result)

        if length > 0 and len(result) > length:
            result = result[0:length]

        return result

    def get_arg_bool(self, name, default=False):
        """
        获取bool型输入
        """
        result = self.get_argument(name, None, True)

        if result is None:
            return default

        result = self.convert_bool(result)

        return result

    def get_arg_int(self, name, default=0, min_val=None, max_val=None):
        """
        获取int型输入
        """
        result = self.get_argument(name, None, True)

        if result is None:
            return default

        result = self.convert_int(result, default)
        result = self.interval_limit(result, min_val, max_val)

        return result

    def get_arg_float(self, name, default=0.0, min_val=None, max_val=None):
        """
        获取float型输入
        """
        result = self.get_argument(name, None, True)

        if result is None:
            return default

        result = self.convert_float(result, default)
        result = self.interval_limit(result, min_val, max_val)

        return result

    def get_arg_json(self, name, default=None, throw_error=False):
        """
        获取json型输入
        """
        result = self.get_argument(name, None, True)

        if result is None:
            result = default
        else:
            try:
                result = self.json_decode(result)
            except:
                result = ErrorData(result) if throw_error else default

        return result

    def get_json_argument(self, name, default=None):

        return self.request.json_arguments.get(name, default)

    def get_json_arguments(self):

        return self.deepcopy(self.request.json_arguments)

    def get_all_arguments(self):

        result = {}

        for key in self.request.arguments.keys():
            result[key] = self.get_argument(key)

        return result

    def write_json(self, chunk, status_code=200):
        """
        输出JSON类型
        """
        self.set_header(r'Content-Type', r'application/json')

        if status_code != 200:
            self.set_status(status_code)

        try:
            response = self.json_encode(chunk)
        except:
            response = None

        return self.finish(response)

    def write_json_error(self, code, error, status_code):

        reponse = {
            r'code': code,
            r'error': error,
        }

        return self.write_json(reponse, status_code)

    def write_png(self, chunk):
        """
        输出PNG类型
        """
        self.set_header(r'Content-Type', r'image/png')

        return self.finish(chunk)

    def Break(self):

        raise Ignore()
