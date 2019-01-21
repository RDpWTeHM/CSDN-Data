"""dblib/__init__.py

TODO: n/a
"""

import os
import sys
from collections import OrderedDict

import json
import copy

import requests

###################################################
#   merge super-spider > Crawler
###################################################
from time import sleep
from abc import ABC, abstractmethod

from .resourcemanage import FakeResourceMange


URL_HEAD = "http://localhost:8010/"
URL_CSDNCRAWLER_API_HEAD = "api/v1/CSDNCrawler/"


class DRFOperate(object):
    '''
    TODO:
       -[o] create, retrieve, update, ... response dict -> self.data
       ------
       -[o] __getattr__ => `.<the item>` -mapping-> self.data["<the item>"]
    '''

    permission = None  # -[o] not support for now
    headers = {"Content-Type": 'application/json'}
    url = URL_HEAD + URL_CSDNCRAWLER_API_HEAD + "userids/"
    head_url = URL_HEAD + URL_CSDNCRAWLER_API_HEAD

    def _handler_requests_result(self, r):
        return r.status_code, r.text

    def get_url(self, detail, kw_belong=None, ):
        if kw_belong and not isinstance(kw_belong, OrderedDict):
            raise ValueError("Please use OrderedDict for generate url")

        try:
            belong_url = self.head_url
            if kw_belong:
                '''{"sites": 'www_csdn_net', "user_ids": 'heheda', }
                '''
                for _ in range(len(kw_belong)):
                    k, v = kw_belong.popitem(last=False)
                    belong_url += k + '/' + v + '/'

            if isinstance(detail, str):
                return belong_url + detail + "/"
            elif isinstance(detail, tuple):
                return belong_url + detail[0] + "/" + "{}".format(detail[1]) + "/"
            else:
                raise ValueError("Please use correct 'detail' type.")
        except ValueError:
            raise
        except Exception as err:
            print(err, file=sys.stderr)
            raise

    def create(self, data):
        r = requests.post(self.get_url(self.api_be[0], self.api_kw_belong),
                          json.dumps(data), headers=self.headers)
        return self._handler_requests_result(r)

    def update(self, data):
        r = requests.put(
            self.get_url(self.api_be, self.api_kw_belong),
            json.dumps(data),
            headers=self.headers)
        return self._handler_requests_result(r)

    def retrieve(self, index=True):
        if index is True and self.api_be[1]:  # retrieve obj's detail
            r = requests.get(
                self.get_url(self.api_be, self.api_kw_belong))
        elif index and index is not True:  # retrieve specific detail
            r = requests.get(
                self.get_url((self.api_be[0], index), self.api_kw_belong))
        elif index is False or not self.api_be[1]:  # retrieve list
            r = requests.get(
                self.get_url(self.api_be[0], self.api_kw_belong))
        else:
            raise ValueError(
                "unexpect 'index': {}@{}".format(type(index), index))
        return self._handler_requests_result(r)


class DBUserID(DRFOperate):
    '''
    demo:
        obj = DBUserID("qq_29757283") =>
            api_be <- ("userids", user_id)
            api_kw_belong <- None

        obj = DBUserID() =>
            api_be <- ('userids', None)
            api_kw_belong <- None

    Note: `.read` 100% open to be used

    TODO:
       -[o] Metaclass to fobidden `.update`
            if using like DBUserID().update(user_id, update_d)
       -[o] Metaclass to fobidden `.create`
            if using like DBUserID(<user_id>).create(dict(<the same user_id>)) (if exist)
            -[o] add method to check the instance user_id in DB or not!
            (DBUserID(<user_id>).create() is OK(exist return <exist>, new return <new>))
            (DBUserID(<user_id>).create(dict(<the other user_id>)) fobidden!)
        ------
        xxxxxx
        ------
          -[o] should build a proxy API mapping django model API!!!!
    '''

    def __init__(self, user_id=None):
        self.api_be = ("userids", user_id)
        self.api_kw_belong = None


# class DBUserIDSubMixin(object):
#     def setupAPI_kw_belong(self, user_id):
#         self.api_kw_belong = OrderedDict({"userids": user_id})


class DBVisualData(DRFOperate):
    def __init__(self, user_id, date=None):
        self.api_be = ("visualdatas", date)
        self.api_kw_belong = OrderedDict({"userids": user_id})


class DBFans(DRFOperate):
    def __init__(self, user_id, index=None):
        self.api_be = ("fanses", index)
        self.api_kw_belong = OrderedDict({"userids": user_id})


class DBFollow(DRFOperate):
    def __init__(self, user_id, index=None):
        self.api_be = ("follows", index)
        self.api_kw_belong = OrderedDict({"userids": user_id})


###################################################
#   merge super-spider > Crawler
###################################################
class CrawlMetaclass(type):
    pass


class Crawl(dict, metaclass=CrawlMetaclass):
    pass


class VisitCrawl(ABC):
    def __init__(self, *args, **kw):
        self.fakeRM = FakeResourceMange()

    @abstractmethod
    def _gen_url(self):
        '''require define crawl url '''

    @abstractmethod
    def _setup_browser(self, browser_type=None):
        if not __debug__:
            from selenium import webdriver
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            if browser_type is None: browser_type = "Chrome"
            _f = getattr(webdriver, browser_type)
            if browser_type == "Chrome":
                capa = DesiredCapabilities().CHROME
                capa["pageLoadStrategy"] = "none"
                from selenium.webdriver.chrome.options import Options
                croptions = Options()
                # __string, = ("user-agent=Mozilla/5.0 "
                #              "(Windows NT 10.0; Win64; x64) "
                #              "AppleWebKit/537.36 (KHTML, like Geoko) "
                #              "Chrome/70.0.3538.102 Safari/537.36", )
                # croptions.add_argument(__string)
                browser = _f(
                    executable_path="/usr/lib/chromium-browser/chromedriver",
                    desired_capabilities=capa,
                    chrome_options=croptions, )
            else:
                browser = _f()
            del _f
        else:
            browser = self.fakeRM.acquire_browser_handler_by_create()
        browser.get(self._gen_url())
        sleep(5)
        self.browser = browser

    @abstractmethod
    def _free_browser(self):
        if not __debug__:
            self.browser.close()
            del self.browser
        else:
            self.fakeRM.release_browser_handler(self.browser)
            del self.browser

    def factory_execute_attrname(self, attrname, *args, **kw):
        methname = 'execute_' + type(attrname).__name__
        meth = getattr(self, methname, None)
        if meth is None:
            return self.generic_factory_execute_attrname(attrname, *args, **kw)
        return meth(*args, **kw)

    #
    # metaclasses to check "class data" exsit?
    #
    def _parse(self):
        d = {}
        for attr in self.data.fields:
            d[attr] = self.factory_execute_attrname(attr)
        return d

    def generic_factory_execute_attrname(self, attrname):
        try:
            elem = self.browser.find_element_by_xpath(
                self.data.executions[attrname]['xpath'])
            if "attribute" in self.data.executions[attrname].keys():
                ret = getattr(elem, self.data.executions[attrname]['attribute'])
            elif "func" in self.data.executions[attrname].keys():
                func = getattr(elem, self.data.executions[attrname]['func'])
                ret = func(*self.data.executions[attrname]['vargs'])
        except Exception:
            print("Error when execute_attrname: {}".format(attrname), file=sys.stderr)
            import traceback; traceback.print_exc();
            raise
        return ret


class Observer(ABC):
    @abstractmethod
    def notify(self):
        """Subject call this func. """


# class Subject(Crawl):


class SubjectCrawl(ABC):
    def __init__(self, *args, **kw):
        VisitCrawl.__init__(self)
        self.__observer = set()

    def register(self, observer_obj):
        self.__observer.add(observer_obj)

    def notifyAll(self, *args, **kw):
        for observer in self.__observer:
            observer.notify(self, *args, **kw)

    def notifyOne(self, observer, *args, **kw):
        return observer.notify(self, *args, **kw)

    def remove(self, observer_obj):
        self.__observer.remove(observer_obj)

    def create(self, observer):
        self._setup_browser(browser_type="Chrome")
        ret = self.notifyOne(observer, self._parse())  # '._parse' come from VisitCrawl
        self._free_browser()
        return ret

    @abstractmethod
    def _monitor(self, browser_type=None):
        """do the monitor job"""
        self._setup_browser(browser_type=browser_type)
        self.notifyAll(self._parse())  # '._parse' come from VisitCrawl

        self._free_browser()

    def run(self):
        self._monitor()


# class Subjects(Subject):
    # pass

