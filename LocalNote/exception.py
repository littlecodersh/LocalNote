#coding=utf8
import sys

from evernote.edam.error.ttypes import EDAMSystemException

def main_wrapper(fn):
    def _main_wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except EDAMSystemException, e:
            if e.errorCode == 19:
                print(u'[INFO] 已达到本小时调用次数显示，再次调用会显示未登录，请等待一小时。')
            else:
                raise e
    return _main_wrapper

