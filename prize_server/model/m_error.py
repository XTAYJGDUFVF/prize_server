# coding=utf-8

import functools


# __all__ = [r'ErrorCode']


_error_code_settings = {

    r'Success':                         (1, r'没有错误'),

    r'Unknown':                         (-1, r'未定义错误'),
    r'Search':                          (-2, r'查找信息失败'),
    r'Database':                        (-3, r'数据保存失败'),
    r'Redis':                           (-4, r'缓存设置失败'),


    r'InvalidParameter':                (-10, r'无效参数'),

    r'AccountNotFound':                 (-20001, r'用户不存在'),
    r'PrizeInfoNotFound':               (-20015, r'奖品信息没有查找到'),
    r'InitialFailed':                   (-20016, r'初始化失败'),
    r'NotFoundUser':                    (-20017, r'没有找到该用户'),
    r'NeedListNotFound':                (-20018, r'抽奖信息没有找到')

}


class _ErrorCode(object):

    def __init__(self):

        self._key_code_map = {}
        self._code_reason_map = {}

    def load_settings(self, settings):

        for key, info in settings.items():
            code = info[0]
            self._key_code_map[key] = code
            self._code_reason_map[code] = info[1]

    def get_error_response(self, code_delegate, extra=None):

        code = code_delegate.code

        extra = code_delegate.extra

        if hasattr(code_delegate, r'error'):
            error = code_delegate.error
        else:
            error = self._code_reason_map[code]

        resp = {r'code': code, r'error': error}

        if extra is not None:
            resp[r'extra'] = extra

        return resp

    def __getattr__(self, name):

        code = self._key_code_map[name]

        code_delegate = _CodeDelegate(code)

        return code_delegate

    def construct_code(self, error_resp):

        code = error_resp.get(r'code', None)
        error = error_resp.get(r'error', None)
        extra = error_resp.get(r'extra', None)

        if code is None or error is None:
            code = self._key_code_map[r'BadErrorFormat']
            code_delegate = _CodeDelegate(code).set_extra(str(error_resp))

        else:
            code_delegate = _CodeDelegate(code)
            setattr(code_delegate, r'error', error)
            if extra is not None:
                code_delegate.set_extra(extra)

        return code_delegate


@functools.total_ordering
class _CodeDelegate(object):

    def __init__(self, code):
        self.code = code
        self.extra = None

    def __eq__(self, other):
        return self.code == other.code

    def __lt__(self, other):
        return self.code < other.code

    def set_extra(self, extra):
        self.extra = extra
        return self

    def __repr__(self):
        return r'{} {}'.format(self.code, self.extra or r'')


ErrorCode = _ErrorCode()
ErrorCode.load_settings(_error_code_settings)


if __name__ == r'__main__':

    print(ErrorCode.Success)
    print(ErrorCode.Unknown)
    print(ErrorCode.Database)

    print(ErrorCode.get_error_response(ErrorCode.Unknown))
