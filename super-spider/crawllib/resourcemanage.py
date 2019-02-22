"""resourcemanage.py

TODO:
  n/a
"""

import sys
import os
import time
from time import sleep

from datetime import datetime
# from datetime import timedelta

# from threading import Thread
import threading
import queue
from queue import Queue

try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException

    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
except ImportError as exc:
    raise ImportError(
        "Couldn't import selenium. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc

from .fakeselenium import Chrome

#####################################################
# pypi.org final-class-0.1.2                        #
# Note: @final only work Python version > 3.6       #
#####################################################
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


##############################################
#             resource mange                 #
##############################################
@final
class BrowserResource(object):
    ''' Resource class
      Issue:
        -[x] total seems not work! -- don't put share value into __init__

      TODO:
        -[o] although it's for daemon processing,
             but still need a quit all browsers function(or usage example).
        -[o] put lend browser-handler recorde, if crash, try "close", and delete instance
    '''

    QBrowser = Queue()
    _browser_state_Lock = threading.Lock()
    _browser_state = {
        "MAX_NUM": 2,
        "total": 0,
        #
        # "lend": {"names": ["weibo-id_heheda", ],
        #          "weibo-id_heheda": {"time": datetime, },
        #         }
        # ADD: slef._browser_state["lend"][
        #          self._browser_state["lend"]["name"][idx]
        #      ] = {"time": datetime}
        # RM: slef._browser_state["lend"].remove(
        #         self._browser_state["lend"]["name"][idx])
        "lend": {"names": [], },
    }
    _LEND_TIME_IDX = "time"

    __manage_run_Lock = threading.Lock()
    __manage_run_flag = False

    def __new__(cls, *args, **kw):  # Singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(BrowserResource, cls).__new__(cls, *args, **kw)
        return cls.instance

    def __init__(self):
        pass

    def __mark_lend_browser_for(self, lend_or_gather, id_browser, plend):
        '''need RLock??
        '''
        if lend_or_gather == "lend":
            plend["names"].append(id_browser)
            plend[id_browser] = {self._LEND_TIME_IDX: datetime.now()}
        elif lend_or_gather == "gather":
            plend["names"].remove(id_browser)
            plend.pop(id_browser)

    def _create_new_browser(self):
        capa = DesiredCapabilities().CHROME
        capa["pageLoadStrategy"] = "none"
        # capa["pageLoadStrategy"] = 'eager'
        from selenium.webdriver.chrome.options import Options
        cr_options = Options()
        # cr_options.headless = True

        #
        # User-Agent
        #
        _system_ver = ["Windows NT 10.0; Win64; x64"]
        _V_537_36 = "537.36"
        _applewebkit_ver = [_V_537_36,        _V_537_36, ]
        _chrome_ver      = ["70.0.3538.102", "71.0.3578.98", ]
        _safari_ver      = [_V_537_36,        _V_537_36, ]

        '''
        def _random_from_list(l):
            from random import randint
            return l[randint(0, len(l) - 1)]
        '''
        from random import randint
        _idx = randint(0, len(_chrome_ver) - 1)

        __string = "user-agent=Mozilla/5.0 " +\
                   "({}) ".format(_system_ver[randint(0, len(_system_ver) - 1)]) + \
                   "AppleWebKit/" + _applewebkit_ver[_idx] + " (KHTML, like Geoko) " +\
                   "Chrome/" + _chrome_ver[_idx] + " " +\
                   "Safari/" + _safari_ver[_idx]
        cr_options.add_argument(__string)

        browser = webdriver.Chrome(
            executable_path="/usr/lib/chromium-browser/chromedriver",
            desired_capabilities=capa,
            chrome_options=cr_options, )
        time.sleep(1)
        return browser

    def __do_check_timeout_consider_as_crash(self):
        with self._browser_state_Lock:
            if __debug__:
                print("[Debug] manage -> print _browser_state first",
                      file=sys.stderr)
                print("[Debug] manage: self._browser_state: ",
                      file=sys.stderr)
                print("\t{!r}\n".format(self._browser_state),
                      file=sys.stderr)

            _lend = self._browser_state["lend"]
            if len(_lend["names"]) > 0:
                for name in _lend["names"]:  # check every browser
                    # lend timeout?
                    lend_time = _lend[name][self._LEND_TIME_IDX]
                    current_time = datetime.now()
                    # time caculate -> datetime.timedelta
                    # > 5 min: empiric value
                    _timeout = 180
                    if abs((current_time - lend_time).seconds) > _timeout:
                        if __debug__:
                            print("timeout {}, do deal with crash {}".format(
                                _timeout, name), file=sys.stderr)
                        # this lent browser crash
                        id_browser = name
                        self.__mark_lend_browser_for(
                            "gather", id_browser, _lend)
                        self._browser_state["total"] -= 1
            else:  # no lend, no need to do anything
                pass

    #
    # r = Resource()
    # t = threading.Thread(target=r.manage(), etc...); t.start()
    #
    def manage(self):
        with self.__manage_run_Lock:
            if self.__manage_run_flag:
                raise RuntimeError("Manage() had been running already!")
            else:  # flas == False, keep run fallow logical.
                self.__manage_run_flag = True

        while True:
            sleep(15)  # check every 10 seconds
            self.__do_check_timeout_consider_as_crash()

    def handler_quit(self):
        with self._browser_state_Lock:
            while True:
                try:
                    browser = self.QBrowser.get(timeout=10)
                    browser.quit()
                except queue.Empty:
                    break

    # browser = None
    # try:
    #     browser = r.acquire_browser_handler_by_create()
    # except:
    #     browser = r.acquire_browser_handler_from_queue()
    # if not browser:
    #     # ...code...
    #     r.release_browser_handler(browser)
    def acquire_browser_handler_by_create(self, name_id=None):
        browser = None
        with self._browser_state_Lock:
            # make sure name_id is only one.
            if self._browser_state["total"] < self._browser_state["MAX_NUM"]:
                try:
                    browser = self._create_new_browser()
                except Exception as err:
                    print("[Debug]: Create new browser error", err, sys.stderr)
                    #
                    # -[o] would cause Lock no-release issue?
                    #
                    raise Exception("Create new browser issue")
                else:  # success
                    # Currently identified browser by session id
                    id_browser = browser.session_id
                    self._browser_state["total"] += 1
                    self.__mark_lend_browser_for(
                        "lend", id_browser, self._browser_state["lend"])
            else:
                raise Exception("can't create more browser, "
                                "reach to MAX Number")
        if browser:
            return browser
        else:
            raise Exception("should not run here")

    def acquire_browser_handler_from_queue(self, name_id=None):
        with self._browser_state_Lock:
            browser = self.QBrowser.get()
            # Currently identified browser by session id
            id_browser = browser.session_id
            self.__mark_lend_browser_for(
                "lend", id_browser, self._browser_state["lend"])

            return browser

    def release_browser_handler(self, browser, name_id=None):
        with self._browser_state_Lock:
            self.QBrowser.put(browser)
            # Currently identified browser by session id
            id_browser = browser.session_id
            self.__mark_lend_browser_for(
                "gather", id_browser, self._browser_state["lend"])

