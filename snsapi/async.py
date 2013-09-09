# coding: utf-8

import types
import time
import threading
from snslog import SNSLog as logger


class AsynchronousThreading(threading.Thread):
    def __init__(self, func, callback=None, args=(), kwargs={}, daemon=False):
        super(AsynchronousThreading, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.daemon = daemon

    def run(self):
        ret = self.func(*self.args, **self.kwargs)
        if self.callback:
            self.callback(ret)


class AsynchronousWithCallBack:
    def __init__(self, instance):
        self._p = instance
        for i in filter(lambda t: type(getattr(self._p, t)) == types.MethodType, dir(self._p)):
            setattr(self, i, self._call_(getattr(self._p, i)))

    def _call_(self, target):
        def func(callback=None, *args, **kwargs):
            AsynchronousThreading(target, callback, args, kwargs).start()
        return func

class AsyncDaemonWithCallBack:
    def __init__(self, target, args, kwargs, callback, sleepsec):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.sleepsec = sleepsec

    def start(self):
        self.started = True
        self._start()

    def _start(self):
        AsynchronousThreading(self.target, self.callback_and_sleep, self.args, self.kwargs, daemon=True).start()

    def stop(self):
        self.started = False

    def callback_and_sleep(self, value):
        if self.callback:
            try:
                self.callback(value)
            except Exception as e:
                logger.warning("Error while executing callback %s" % (str(e)))
        if self.started:
            for i in range(self.sleepsec):
                time.sleep(1)
                if not self.started:
                    break
            if self.started:
                self._start()
