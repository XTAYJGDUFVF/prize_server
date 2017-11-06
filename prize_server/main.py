# coding=utf-8

import asyncio
import os
import platform
import signal

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import gen_log
from tornado.netutil import bind_sockets
from tornado.options import options
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.process import cpu_count, fork_processes
from tornado.web import Application
from config import Config
Config.read(r'./config.conf')

import router
from service import Service


class Entry():

    def __init__(self):

        self._is_linux = (platform.system() == r'Linux')

        self._process_id = 0
        self._process_num = cpu_count()

        self._sockets = bind_sockets(Config.Port)

        if self._is_linux:

            self._process_id = fork_processes(self._process_num)

        self._init_options()

        AsyncIOMainLoop().install()

        self._event_loop = asyncio.get_event_loop()
        self._server = HTTPServer(Application(**self._settings))

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        from model.base import initialize as model_initialize

        IOLoop.instance().run_sync(model_initialize)

    def _init_options(self):

        self._settings = {
            r'handlers': router.urls,
            r'debug': Config.Debug,
            r'gzip': Config.GZip,
        }

        if(Config.LogLevel):
            options.logging = Config.LogLevel

        if(Config.LogFilePath):

            if(not os.path.exists(Config.LogFilePath)):
                os.makedirs(Config.LogFilePath)

            options.log_rotate_mode = r'time'
            options.log_rotate_when = r'midnight'
            options.log_file_num_backups = Config.LogFileBackups

            options.log_file_prefix = r'{}/all.log'.format(
                Config.LogFilePath
            )

        options.parse_command_line()

    def start(self):

        self._server.add_sockets(self._sockets)

        gen_log.info(r'Startup http server No.{}, pid {}'.format(self._process_id, os.getpid()))

        if self._is_linux and self._process_id == 0:
            Service().run()
            gen_log.info(r'Startup service on No.{}, pid {}'.format(self._process_id, os.getpid()))

        self._event_loop.run_forever()

    def stop(self, code=0):

        self._server.stop()

        self._event_loop.stop()

        gen_log.info(r'Shutdown http server No.{} (code:{}), pid {}'.format(self._process_id, code, os.getpid()))


if __name__ == r'__main__':

    Entry().start()
