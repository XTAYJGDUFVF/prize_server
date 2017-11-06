# coding=utf-8

import json
from tornado.gen import coroutine
from tornado.log import app_log

from util.util import Utils
from model.base import MySQLPool, MCachePool
from config import Config


base_data = {
    r'server_uuid': None,
    r'up_time': Utils.timestamp()
}

@coroutine
def report_status():

    if not base_data[r'server_uuid']:
        ip_resp = yield Utils.http_request(Config.IpEchoInterface, method=r'GET')
        if ip_resp and ip_resp.code >= 200 and ip_resp.code < 300:
            base_data[r'server_uuid'] = str(ip_resp.body, r'utf-8')

    if not base_data[r'server_uuid']:
        app_log.warning(r"get server ip failed, status report abort")
        return

    data = {
        r'server_type': r'account_service',
    }

    data.update(base_data)

    status = Utils.get_machine_status()
    data.update(status)

    mysql_conn = MySQLPool().get_conn_status()
    data[r'mysql_conn'] = json.dumps(mysql_conn)

    redis_conn = MCachePool().get_conn_status()
    data[r'redis_conn'] = json.dumps(redis_conn)

    resp = yield Utils.http_request(Config.MaintainServiceInterface + r'server_status', method=r'POST', body=data, style=r'JSON')

    if not resp or not (resp.code >= 200 and resp.code < 300):
        app_log.error(r"status report error")
