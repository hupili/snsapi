#-*- encoding: utf-8 -*-
import inspect
import os
import glob
import snsapi.snsbase


fpath = os.path.abspath(__file__)
for i in glob.glob(os.path.dirname(fpath) + "/*.py"):
    if i[-11:] == "__init__.py":
        continue
    ss = __import__(__name__ + '.' + i[:-3].split('/')[-1], fromlist=["*"])
    for i in dir(ss):
        if inspect.isclass(getattr(ss, i)) and issubclass(getattr(ss, i), snsapi.snsbase.SNSBase) and getattr(ss, i) != snsapi.snsbase.SNSBase:
            globals()[i] = getattr(ss, i)
