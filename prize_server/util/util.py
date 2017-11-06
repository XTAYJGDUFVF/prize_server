# coding=utf-8

import base64
import binascii
import calendar
import copy
import functools
import hashlib
import hmac
import math
import pickle
import random
import re
import socket
import string
import textwrap
import time
import unicodedata
import urllib
import uuid
import xml.dom.minidom
import zlib
from collections import Iterable, OrderedDict
from datetime import datetime, timedelta

import psutil
from tornado.concurrent import Future
from tornado.escape import utf8, to_basestring, json_decode, json_encode
from tornado.gen import coroutine, sleep
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.httputil import url_concat
from tornado.ioloop import IOLoop
from tornado.log import app_log
from tornado.netutil import is_valid_ip
from tornado.process import task_id, cpu_count
from tornado.util import import_object

import xmltodict
from sdk import jwt
from .metaclass import SingletonMetaclass


class Singleton(metaclass=SingletonMetaclass):

    pass


class FutureWithTimeout(Future):

    def __init__(self, delay):

        super().__init__()

        self._timeout = Utils._add_timeout(delay, self._set_done)

        self.add_done_callback(self._clear_timeout)

    def _clear_timeout(self, future=None):

        if self._timeout is not None:

            Utils._remove_timeout(self._timeout)

            self._timeout = None


class Utils():

    SAFE_STRING_BASE = r'2346789BCEFGHJKMPQRTVWXY'

    math = math
    random = random
    textwrap = textwrap

    log = app_log

    import_object = staticmethod(import_object)
    task_id = staticmethod(task_id)
    cpu_count = staticmethod(cpu_count)
    is_valid_ip = staticmethod(is_valid_ip)

    urlparse = urllib.parse
    url_concat = staticmethod(url_concat)

    deepcopy = staticmethod(copy.deepcopy)

    func_partial = staticmethod(functools.partial)

    randint = staticmethod(random.randint)
    randstr = staticmethod(random.sample)

    utf8 = staticmethod(utf8)
    basestring = staticmethod(to_basestring)

    sleep = staticmethod(sleep)

    json_encode = staticmethod(json_encode)
    json_decode = staticmethod(json_decode)

    @staticmethod
    def _add_timeout(delay, _callable, *args, **kwargs):

        return IOLoop.current().call_later(delay, _callable, *args, **kwargs)

    @staticmethod
    def _remove_timeout(timeout):

        return IOLoop.current().remove_timeout(timeout)

    @classmethod
    def get_machine_status(cls):

        net_io_info = psutil.net_io_counters()

        status = {
            r'cpu_percent': round(psutil.cpu_percent() / 100.0, 4),
            r'mem_percent': round(psutil.virtual_memory().percent / 100.0, 4),
            r'bytes_sent':  net_io_info.bytes_sent,
            r'bytes_recv': net_io_info.bytes_recv
        }

        return status

    @classmethod
    def remove_mb4(cls, short_str, rep_char=r''):

        result_char_lst = []

        for c in short_str:
            if c >= '\uffff':
                c = rep_char
            result_char_lst.append(c)

        return r''.join(result_char_lst)

    @classmethod
    def today(cls, origin=False):

        result = datetime.today()

        return result.replace(hour=0, minute=0, second=0, microsecond=0) if origin else result

    @classmethod
    def utcnow(cls, origin=False):

        result = datetime.utcnow()

        return result.replace(hour=0, minute=0, second=0, microsecond=0) if origin else result

    @classmethod
    def timestamp(cls):

        return int(time.time())

    @classmethod
    def milli_timestamp(cls):

        return int(time.time() * 1000)

    __FALSE_VALS = {r'null', r'none', r'nil', r'false', r'0', r'', False, 0}

    @classmethod
    def convert_bool(cls, val):

        if isinstance(val, str):
            val = val.lower()

        return val not in cls.__FALSE_VALS

    @classmethod
    def convert_int(cls, val, default=0):

        result = default

        try:
            if not isinstance(val, float):
                result = int(val)
        except:
            pass

        return result

    @classmethod
    def convert_float(cls, val, default=0.0):

        result = default

        try:
            if not isinstance(val, float):
                result = float(val)
        except:
            pass

        return result

    @classmethod
    def interval_limit(cls, val, min_val, max_val):

        result = val

        if min_val is not None:
            result = max(result, min_val)

        if max_val is not None:
            result = min(result, max_val)

        return result

    @classmethod
    def split_int(cls, val, sep=r',', minsplit=0, maxsplit=-1):

        result = [int(item.strip()) for item in val.split(sep, maxsplit) if item.strip().isdigit()]

        fill = minsplit - len(result)

        if fill > 0:
            result.extend(0 for _ in range(fill))

        return result

    @classmethod
    def join_int(cls, iterable, sep=r','):

        result = []

        for item in iterable:

            cls = type(item)

            if cls is int:

                result.append(str(item))

            elif cls is str:

                item = item.strip()

                if item.isdigit():
                    result.append(item)

        return sep.join(result)

    @classmethod
    def split_str(cls, val, sep=r'|', minsplit=0, maxsplit=-1):

        result = [item.strip() for item in val.split(sep, maxsplit)]

        fill = minsplit - len(result)

        if fill > 0:
            result.extend(r'' for _ in range(fill))

        return result

    @classmethod
    def join_str(cls, iterable, sep=r'|'):

        return sep.join(str(val).replace(sep, r'') for val in iterable)

    @classmethod
    def list_extend(cls, iterable, val):

        if cls.is_iterable(val, True):
            iterable.extend(val)
        else:
            iterable.append(val)

    @classmethod
    def str_len(cls, str_val):

        result = 0

        for val in str_val:

            if unicodedata.east_asian_width(val) in (r'A', r'F', r'W'):
                result += 2
            else:
                result += 1

        return result

    @classmethod
    def sub_str(cls, str_val, length, suffix=r'...'):

        result = []
        strlen = 0

        for val in str_val:

            if unicodedata.east_asian_width(val) in (r'A', r'F', r'W'):
                strlen += 2
            else:
                strlen += 1

            if strlen > length:

                if suffix:
                    result.append(suffix)

                break

            result.append(val)

        return r''.join(result)

    @classmethod
    def re_match(cls, pattern, value):

        result = re.match(pattern, value)

        return True if result else False

    @classmethod
    def randhit(cls, iterable, probs):

        if not cls.is_iterable(probs):
            probs = [probs(val) for val in iterable]

        prob_hit = 0
        prob_sum = cls.randint(0, sum(probs))

        for index in range(0, len(probs)):

            prob_hit += probs[index]

            if prob_hit > prob_sum:
                break

        return iterable[index] if index < len(iterable) else None

    @classmethod
    def ip2int(cls, val):

        try:
            return int(binascii.hexlify(socket.inet_aton(val)), 16)
        except socket.error:
            return int(binascii.hexlify(socket.inet_pton(socket.AF_INET6, val)), 16)

    @classmethod
    def int2ip(cls, val):

        try:
            return socket.inet_ntoa(binascii.unhexlify(r'%08x' % val))
        except socket.error:
            return socket.inet_ntop(socket.AF_INET6, binascii.unhexlify(r'%032x' % val))

    @classmethod
    def time2stamp(cls, timestr, format_type=r'%Y-%m-%d %H:%M:%S'):

        return time.mktime(time.strptime(timestr, format_type))

    @classmethod
    def stamp2time(cls, stamp=None, format_type=r'%Y-%m-%d %H:%M:%S'):

        if stamp is None:
            stamp = cls.timestamp()

        return time.strftime(format_type, time.localtime(stamp))

    @classmethod
    def radix24(cls, val):

        base = cls.SAFE_STRING_BASE

        num = int(val)

        if num <= 0:
            return base[num]

        result = ''

        while(num > 0):
            num, rem = divmod(num, 24)
            result = r'{0}{1}'.format(base[rem], result)

        return result

    @classmethod
    def radix36(cls, val, align=0):

        base = string.digits + string.ascii_uppercase

        num = int(val)

        if num <= 0:
            return base[num]

        result = ''

        while(num > 0):
            num, rem = divmod(num, 36)
            result = r'{0}{1}'.format(base[rem], result)

        return r'{0:0>{1:d}s}'.format(result, align)

    @classmethod
    def radix62(cls, val, align=0):

        base = string.digits + string.ascii_letters

        num = int(val)

        if num <= 0:
            return base[num]

        result = ''

        while(num > 0):
            num, rem = divmod(num, 62)
            result = r'{0}{1}'.format(base[rem], result)

        return r'{0:0>{1:d}s}'.format(result, align)

    @classmethod
    def xml_encode(cls, dict_val, root_tag=r'root'):

        xml_doc = xml.dom.minidom.Document()

        root_node = xml_doc.createElement(root_tag)
        xml_doc.appendChild(root_node)

        def _convert(_doc, _node, _dict):

            for key, val in _dict.items():

                temp = _doc.createElement(key)

                if isinstance(val, dict):
                    _convert(_doc, temp, val)
                else:
                    temp.appendChild(_doc.createTextNode(str(val)))

                _node.appendChild(temp)

        _convert(xml_doc, root_node, dict_val)

        return xml_doc

    @classmethod
    def xml_decode(cls, val):

        return xmltodict.parse(cls.utf8(val))

    @classmethod
    def b32_encode(cls, val, standard=False):

        val = cls.utf8(val)

        result = base64.b32encode(val)

        if not standard:
            result = result.rstrip(b'=')

        return cls.basestring(result)

    @classmethod
    def b32_decode(cls, val, standard=False, for_bytes=False):

        val = cls.utf8(val)

        if not standard:

            num = len(val) % 8

            if num > 0:
                val = val + b'=' * (8 - num)

        result = base64.b32decode(val)

        if for_bytes:
            return result
        else:
            return cls.basestring(result)

    @classmethod
    def b64_encode(cls, val, standard=False):

        val = cls.utf8(val)

        if standard:

            result = base64.b64encode(val)

        else:

            result = base64.urlsafe_b64encode(val)

            result = result.rstrip(b'=')

        return cls.basestring(result)

    @classmethod
    def b64_decode(cls, val, standard=False, for_bytes=False):

        val = cls.utf8(val)

        if standard:

            result = base64.b64decode(val)

        else:

            num = len(val) % 4

            if num > 0:
                val = val + b'=' * (4 - num)

            result = base64.urlsafe_b64decode(val)

        if for_bytes:
            return result
        else:
            return cls.basestring(result)

    @classmethod
    def jwt_encode(cls, val, key):

        result = jwt.encode(val, key)

        return cls.basestring(result)

    @classmethod
    def jwt_decode(cls, val, key):

        val = cls.utf8(val)

        return jwt.decode(val, key)

    @classmethod
    def pickle_dumps(cls, val):

        stream = pickle.dumps(val)

        result = zlib.compress(stream)

        return result

    @classmethod
    def pickle_loads(cls, val):

        stream = zlib.decompress(val)

        result = pickle.loads(stream)

        return result

    @classmethod
    def uuid1(cls, node=None, clock_seq=None):

        return uuid.uuid1(node, clock_seq).hex

    @classmethod
    def crc32(cls, val):

        val = cls.utf8(val)

        return binascii.crc32(val)

    @classmethod
    def md5(cls, val):

        val = cls.utf8(val)

        return hashlib.md5(val).hexdigest()

    @classmethod
    def md5_u32(cls, val):

        val = cls.utf8(val)

        return int(hashlib.md5(val).hexdigest(), 16) >> 96

    @classmethod
    def md5_u64(cls, val):

        val = cls.utf8(val)

        return int(hashlib.md5(val).hexdigest(), 16) >> 64

    @classmethod
    def sha1(cls, val):

        val = cls.utf8(val)

        return hashlib.sha1(val).hexdigest()

    @classmethod
    def sha256(cls, val):

        val = cls.utf8(val)

        return hashlib.sha256(val).hexdigest()

    @classmethod
    def sha512(cls, val):

        val = cls.utf8(val)

        return hashlib.sha512(val).hexdigest()

    @classmethod
    def hmac_md5(cls, key, msg):

        key = cls.utf8(key)
        msg = cls.utf8(msg)

        result = hmac.new(key, msg, r'md5').digest()

        result = base64.b64encode(result)

        return cls.basestring(result)

    @classmethod
    def hmac_sha1(cls, key, msg):

        key = cls.utf8(key)
        msg = cls.utf8(msg)

        result = hmac.new(key, msg, r'sha1').digest()

        result = base64.b64encode(result)

        return cls.basestring(result)

    @classmethod
    def ordered_dict(cls, val=None):

        if val is None:
            return OrderedDict()
        else:
            return OrderedDict(sorted(val.items(), key=lambda x: x[0]))

    @classmethod
    def is_iterable(cls, obj, standard=False):

        if standard:
            result = isinstance(obj, Iterable)
        else:
            result = isinstance(obj, (list, tuple,))

        return result

    @classmethod
    def luhn(cls, val):

        result = False

        val = val[::-1].strip()

        if val.isdigit():

            check_total = 0

            for index in range(0, len(val)):

                if index & 1:
                    temp = int(val[index]) * 2
                    check_total += (temp if temp < 10 else temp - 9)
                else:
                    check_total += int(val[index])

            result = (check_total % 10 == 0)

        return result

    @classmethod
    def append_luhn(cls, val):

        result = None

        _val = val[::-1].strip()
        _val = r'{0:s}{1:s}'.format(r'0', _val)

        if(_val.isdigit()):

            check_total = 0

            for index in range(0, len(_val)):

                if(index & 1):
                    temp = int(_val[index]) * 2
                    check_total += (temp if temp < 10 else temp - 9)
                else:
                    check_total += int(_val[index])

            check_bit = check_total % 10

            if(check_bit > 0):
                result = r'{0:s}{1:d}'.format(val, 10 - check_bit)
            else:
                result = r'{0:s}0'.format(val)

        return result

    @classmethod
    def identity_card(cls, val):

        result = False

        val = val.strip().upper()

        if len(val) == 18:

            weight_factor = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1,)

            verify_list = r'10X98765432'

            check_total = 0

            for index in range(0, 17):
                check_total += int(val[index]) * weight_factor[index]

            result = (verify_list[check_total % 11] == val[17])

        return result

    @classmethod
    def params_join(cls, params, filters=[]):

        if filters:
            params = {key: val for key, val in params.items() if key not in filters}

        return r'&'.join(r'{0}={1}'.format(key, val) for key, val in sorted(params.items(), key=lambda x: x[0]))

    @classmethod
    def params_sign(cls, *args, **kwargs):

        result = []

        if args:
            result.extend(str(val) for val in args)

        if kwargs:
            result.extend(cls.params_join(kwargs))

        return cls.md5(r'&'.join(result))

    @classmethod
    @coroutine
    def http_request(cls, url, params=None, method=r'GET', *, headers=None, body=None, style=None, **kwargs):

        if body is None and method.upper() in [r'POST', r'PUT']:
            body = r''

        response = yield cls._fetch_url(url, params, method, headers=headers, body=body, **kwargs)

        if response and response.body:

            try:

                if isinstance(style, str):
                    style = style.upper()

                if style == r'JSON':
                    result = cls.json_decode(response.body)
                elif style == r'XML':
                    result = cls.xml_decode(response.body)
                elif style == r'TEXT':
                    result = cls.basestring(response.body)
                else:
                    result = response.body

                setattr(response, r'result', result)

            except Exception as err:

                cls.log.exception(r'{0} => {1}'.format(err, response.body))

            else:

                if style in (r'JSON', r'XML', r'TEXT'):
                    cls.log.debug(response.body)

        return response

    @classmethod
    @coroutine
    def fetch_url(cls, url, params=None, method=r'GET', *, headers=None, body=None, style=r'JSON', **kwargs):

        result = None

        response = yield cls._fetch_url(url, params, method, headers=headers, body=body, **kwargs)

        if response and response.body:

            try:

                if isinstance(style, str):
                    style = style.upper()

                if style == r'JSON':
                    result = cls.json_decode(response.body)
                elif style == r'XML':
                    result = cls.xml_decode(response.body)
                elif style == r'TEXT':
                    result = cls.basestring(response.body)
                else:
                    result = response.body

            except Exception as err:

                cls.log.exception(r'{0} => {1}'.format(err, response.body))

            else:

                if style in (r'JSON', r'XML', r'TEXT'):
                    cls.log.debug(response.body)

        return result

    _HTTP_ERROR_AUTO_RETRY = 5
    _HTTP_CONNECT_TIMEOUT = 5.0
    _HTTP_REQUEST_TIMEOUT = 10.0

    @classmethod
    @coroutine
    def _fetch_url(cls, url, params=None, method=r'GET', *, headers=None, body=None, **kwargs):

        if params:
            url = cls.url_concat(url, params)

        if headers is None:
            headers = {}

        if isinstance(body, dict):

            content_type = headers.get(r'Content-Type', None)

            if content_type is None:
                headers[r'Content-Type'] = r'application/x-www-form-urlencoded'
                body = cls.urlparse.urlencode(body)
            elif content_type == r'application/json':
                body = cls.json_encode(body)

        result = None

        for _ in range(0, cls._HTTP_ERROR_AUTO_RETRY):

            try:

                client = AsyncHTTPClient()

                if r'connect_timeout' not in kwargs:
                    kwargs[r'connect_timeout'] = cls._HTTP_CONNECT_TIMEOUT

                if r'request_timeout' not in kwargs:
                    kwargs[r'request_timeout'] = cls._HTTP_REQUEST_TIMEOUT

                result = yield client.fetch(HTTPRequest(url, method.upper(), headers, body, **kwargs))

            except HTTPError as err:

                result = err.response

                if err.code < 500:
                    break
                else:
                    yield cls.sleep(1)

            except Exception as err:

                yield cls.sleep(1)

            else:

                break

        return result

    @classmethod
    def get_today_region(cls, today=None):

        if today is None:
            today = cls.today(True)

        start_date = today
        end_date = today + timedelta(days=1)

        start_time = int(time.mktime(start_date.timetuple()))
        end_time = int(time.mktime(end_date.timetuple())) - 1

        return (start_time, end_time)

    @classmethod
    def get_month_region(cls, today=None):

        if today is None:
            today = cls.today(True)

        start_date = today.replace(day=1)

        _, days_in_month = calendar.monthrange(start_date.year, start_date.month)

        end_date = start_date + timedelta(days=days_in_month)

        start_time = int(time.mktime(start_date.timetuple()))
        end_time = int(time.mktime(end_date.timetuple())) - 1

        return (start_time, end_time)

    @classmethod
    def get_week_region(cls, today=None):

        if today is None:
            today = cls.today(True)

        week_pos = today.weekday()

        start_date = today - timedelta(days=week_pos)
        end_date = today + timedelta(days=(7 - week_pos))

        start_time = int(time.mktime(start_date.timetuple()))
        end_time = int(time.mktime(end_date.timetuple())) - 1

        return (start_time, end_time)

    def debug(self, content, *args):

        app_log.debug(content.format(*args))

    # 整型时间戳转结构化时间
    @classmethod
    def int_struct(cls, int_time):

        time_local = time.localtime(int_time)

        st = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

        return st

    # 结构化时间转为时间戳
    @classmethod
    def struct_int(cls, struct_time):

        timeArray = time.strptime(struct_time, "%Y-%m-%d %H:%M:%S")

        timestamp = time.mktime(timeArray)

        return int(timestamp)

    # 获取当天0点的时间戳
    @classmethod
    def today_zero(cls):

        t = time.localtime(time.time())

        time_night = time.mktime(time.strptime(time.strftime('%Y-%m-%d 0:0:0', t), '%Y-%m-%d %H:%M:%S'))

        return time_night
