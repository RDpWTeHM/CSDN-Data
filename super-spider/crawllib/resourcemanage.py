"""resourcemanage.py

TODO:
  n/a
"""

import sys
import os
import time
import threading

from .fakeselenium import Chrome

#
# pypi.org final-class-0.1.2
# Note: @final only work Python version > 3.6
#
from typing import Type, TypeVar

T = TypeVar('T', bound=Type)


def _init_subclass(cls: T, *args, **kwargs) -> None:
    raise TypeError('Subclassing final classes is restricted')


def final(cls: T) -> T:
    """Marks class as `final`, so it won't have any subclasses."""
    setattr(cls, '__init_subclass__', classmethod(_init_subclass))
    return cls

# END final-class-0.1.2


@final
class FakeResourceMange(object):
    __manage_run_Lock = threading.Lock()
    __manage_run_flag = False

    def __new__(cls, *args, **kw):  # Singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(FakeResourceMange, cls).__new__(cls, *args, **kw)
        return cls.instance

    def __init__(self):
        pass

    def __do_check_timeout_consider_as_crash(self):
        while True:
            print("'{}' do check running at backend".format(
                type(self).__name__),
                file=sys.stderr)
            time.sleep(30)

    def manage(self):
        with self.__manage_run_Lock:
            if self.__manage_run_flag:
                raise RuntimeError(
                    "{} > manage() had been running backend already!".format(
                        type(self).__name__)
                )
            else:  # flas == False, keep run fallow logical.
                self.__manage_run_flag = True

        t = threading.Thread(
            target=self.__do_check_timeout_consider_as_crash)
        t.setDaemon(True)
        t.start()

    def acquire_browser_handler_by_create(self, name_id=None):
        browser = Chrome()
        return browser

    def acquire_browser_handler_from_queue(self, name_id=None):
        return Chrome()

    def release_browser_handler(self, browser, name_id=None):
        return True


class ResourceManage(object):
    pass
