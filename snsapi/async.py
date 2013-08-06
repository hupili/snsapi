# coding: utf-8

import types
import time
import threading


class AsynchronousThreading(threading.Thread):
    def __init__(self, func, callback=None, args=(), kwargs={}):
        super(AsynchronousThreading, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.callback = callback

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
        AsynchronousThreading(self.target, self.callback_and_sleep, self.args, self.kwargs).start()

    def stop(self):
        self.started = False

    def callback_and_sleep(self, value):
        if self.callback:
            try:
                self.callback(value)
            except:
                pass
        if self.started:
            if self.sleepsec > 0:
                time.sleep(self.sleepsec)
            self._start()
