# coding=utf-8

from tornado.gen import coroutine

from .util import Utils, FutureWithTimeout
from .context import Transaction


class EventObserver():

    def __init__(self, asyc_task,  *callables):

        self._async_task = asyc_task

        self._callables = {id(_callable): _callable for _callable in callables}

    def __del__(self):

        self._callables.clear()

        self._callables = None

    def __call__(self, *args, **kwargs):

        for _callable in self._callables.values():
            self._async_task.add_timeout(0, _callable, *args, **kwargs)

    @property
    def is_valid(self):

        return len(self._callables) > 0

    def add(self, _callable):

        result = False

        _id = id(_callable)

        if(_id not in self._callables):
            self._callables[_id] = _callable
            result = True

        return result

    def remove(self, _callable):

        result = False

        _id = id(_callable)

        if(_id in self._callables):
            del self._callables[_id]
            result = True

        return result


class EventDispatcher(Utils):

    def __init__(self):

        self._observers = {}

    def dispatch(self, _type, *args, **kwargs):

        self.log.debug(r'dispatch event {0} {1} {2}'.format(_type, args, kwargs))

        if(_type in self._observers):
            self._observers[_type](*args, **kwargs)

    def add_listener(self, async_task,  _type, _callable):

        self.log.debug(r'add event listener => type({0}) function({1})'.format(_type, id(_callable)))

        result = False

        if(_type in self._observers):
            result = self._observers[_type].add(_callable)
        else:
            self._observers[_type] = EventObserver(async_task, _callable)
            result = True

        return result

    def remove_listener(self, _type, _callable):

        self.log.debug(r'remove event listener => type({0}) function({1})'.format(_type, id(_callable)))

        result = False

        if(_type in self._observers):

            observer = self._observers[_type]

            result = observer.remove(_callable)

            if(not observer.is_valid):
                del self._observers[_type]

        return result


class DistributedEventABC(EventDispatcher):

    def __init__(self, event_bus_channel, secret, cache_pool):

        super().__init__()

        self._channels = []

        self.event_bus_channel = event_bus_channel

        self.secret = secret

        self._cache_pool = cache_pool

    def initialize(self):

        for _id in range(0, self.event_bus_channel):

            channel = r'event_bus_{0}'.format(
                self.md5(
                    r'_'.join([str(_id), self.secret])
                )
            )

            self._channels.append(channel)

            self._event_listener(channel)

    @coroutine
    def _event_listener(self, channel):

        self.log.debug(r'Event channel monitored ==> {0}'.format(channel))

        while(True):

            try:

                cache = self._cache_pool.get_client()

                listener, = yield cache.subscribe(channel)

                while(yield listener.wait_message()):
                    self._event_assigner(channel, (yield listener.get()))

            except:

                yield self.sleep(1)

    def _event_assigner(self, channel, message):

        message = self.pickle_loads(message)

        self.log.debug(r'event handling => channel({0}) message({1})'.format(channel, message))

        _type = message.get(r'type', r'')
        args = message.get(r'args', [])
        kwargs = message.get(r'kwargs', {})

        if(_type in self._observers):
            self._observers[_type](*args, **kwargs)

    @coroutine
    def dispatch(self, _type, *args, cache=None, **kwargs):

        if(cache is None):
            cache = self._cache_pool.get_client()

        channel = self.random.choice(self._channels)

        message = {
            r'type': _type,
            r'args': args,
            r'kwargs': kwargs,
        }

        self.log.debug(r'event dispatch => channel({0}) message({1})'.format(channel, message))

        result = yield cache.publish(channel, self.pickle_dumps(message))

        return result


class EventWaiter(FutureWithTimeout):

    def __init__(self, dispatcher, delay, buffer_time=0):

        super().__init__(delay)

        self._dispatcher = dispatcher
        self._transaction = Transaction()

        self._buffer_time = buffer_time
        self._buffer_data = []

    def listen(self, *types):

        for _type in types:

            handler = Utils.func_partial(self._event_handler, _type)

            if(self._dispatcher.add_listener(_type, handler)):
                self._transaction.add(self._dispatcher.remove_listener, _type, handler)

        return self

    def _set_done(self):

        if(not self.running()):
            return

        if(self._transaction is not None):
            self._transaction.rollback()

        self._clear_timeout()

        self._result = self._buffer_data

        super()._set_done()

    def _event_handler(self, _type, *args, **kwargs):

        if(not self.running()):
            return

        event_data = self._merge_event_data(_type, *args, **kwargs)

        self._buffer_data.append(event_data)

        if(self._buffer_time > 0):

            if(len(self._buffer_data) == 1):
                self._clear_timeout()
                Utils._add_timeout(self._buffer_time, self._set_done)

        else:

            self._set_done()

    def _merge_event_data(self, _type, *args, **kwargs):

        event_data = {
            r'type': _type,
            r'args': args,
            r'kwargs': kwargs,
        }

        return event_data
