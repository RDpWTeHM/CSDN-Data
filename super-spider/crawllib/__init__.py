""" __init__.py

"""

from time import sleep
import sys
import os
from abc import ABC, abstractmethod

from .resourcemanage import BrowserResource
from .resourcemanage import FakeResourceMange


class CrawlMetaclass(type):
    pass


class Crawl(dict, metaclass=CrawlMetaclass):
    pass


class VisitCrawl(ABC):
    def __init__(self, *args, **kw):
        if not __debug__:
            self.brrs = BrowserResource()
        else:
            self.fakeRM = FakeResourceMange()

    @abstractmethod
    def _gen_url(self):
        '''require define crawl url '''

    @abstractmethod
    def _setup_browser(self, browser_type=None):
        browser = None
        if not __debug__:
            # -[x] browser_id as input-parameter, reference old CSDNData code.
            # no input-parameter specific browser_id
            try:
                browser = self.brrs.acquire_browser_handler_by_create()
            except Exception:
                browser = self.brrs.acquire_browser_handler_from_queue()
        else:
            browser = self.fakeRM.acquire_browser_handler_by_create()

        # -[o] .get(url) here is not apposite
        browser.get(self._gen_url())
        if not __debug__:
            sleep(5)
        self.browser = browser

    @abstractmethod
    def _free_browser(self):
        if not __debug__:
            self.brrs.release_browser_handler(self.browser)
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
        try:
            self.notifyAll(self._parse())  # '._parse' come from VisitCrawl
        except Exception:
            import traceback; traceback.print_exc();
        finally:
            self._free_browser()

    def run(self):
        self._monitor()


# class Subjects(Subject):
    # pass
