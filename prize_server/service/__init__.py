# coding=utf-8

from tornado.ioloop import IOLoop
from util.task import RepeatTask
from util.util import Singleton

from .task import report_status


_task_settings = [
    # (30, report_status),
]


class Service(Singleton):

    def __init__(self):

        self._task_settings = []

    def load_settings(self, task_settings):

        self._task_settings = task_settings

    def run(self):

        for task_info in self._task_settings:

            report_task = RepeatTask(task_info[0], task_info[1])
            loop = IOLoop.current()
            loop.call_later(0, report_task.run)

Service().load_settings(_task_settings)
