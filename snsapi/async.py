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
