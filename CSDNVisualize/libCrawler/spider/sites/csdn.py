""" handler crawler CSDN site.

TODO:
  -[x] sys.stdout.write() in this file x - logging
"""
import sys
import time
from time import sleep
from time import ctime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import logging


class PageSource():
    '''要做成不用实例化可调用的吗？ '''

    def __init__(self, _browser, timeout=30):
        self.browser = _browser
        self.timeout = timeout
        self.browser.implicitly_wait(timeout)
        self.browser.set_script_timeout(timeout)
        self.browser.set_page_load_timeout(timeout)

    def getPageSourceBy(self, url):
        self.browser.get(url)
        return self.browser.page_source


class HomePageSource(PageSource):
    def __init__(self, _browser, timeout=30):
        super().__init__(_browser, timeout=timeout)

    def getPageSourceBy(self, _url):
        self.browser.get(_url)
        # try:  # 在这个位置真的需要捕获吗？
        if True:
            WebDriverWait(self.browser, self.timeout).until(
                EC.presence_of_element_located((By.ID, 'att_btn')))
            # thisThreadBrowser.execute_script("window.stop();")
            for follow_tag in self.browser.find_elements_by_tag_name("span"):
                if "关注" in follow_tag.text:
                    follow_tag.click()
                    break
            time.sleep(0.2)
            return self.browser.page_source
        # except TimeoutException:
            # pass


class BlogPageSource(PageSource):
    def __init__(self, _browser, timeout=30):
        super().__init__(_browser, timeout=timeout)

    def getPageSourceBy(self, _url):
        self.browser.get(_url)
        time.sleep(0.4)
        WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((By.ID, "btnAttent"))
        )
        return self.browser.page_source


class ArticlesPageSources(BlogPageSource):
    def __init__(self, _browser, timeout=30):
        super().__init__(_browser, timeout=timeout)

    def getPageSourcesBy(self, _url):
        '''_url is the first blog page '''
        page_sources = list()

        self.browser.get(_url)
        WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-pager"))
        )

        _ = [class_page.text for class_page in self.browser.find_elements_by_class_name("ui-pager")]
        MAX_PAGER = list()
        for coverInt in _:
            try:
                MAX_PAGER.append(int(coverInt))
            except ValueError:
                pass
        MAX_PAGER = max(MAX_PAGER)
        logging.info("MAX_PAGER: {!r}".format(MAX_PAGER))

        for _ in range(MAX_PAGER - 1):  # first page had be loaded
            page_sources.append(self.browser.page_source)
            # 除非是在性能好的主机上运行，否则浏览器加载 CSDN blog 页面没那么快，
            # 所以“ui-pager” 出现后，多等一两秒也没有关系，反而可能不容易出 bug。
            time.sleep(1)
            self.browser.execute_script("window.stop();")

            nextpage_tags = self.browser.find_elements_by_tag_name("li")

            _url = self.browser.current_url
            try:
                for nextpage_tag in nextpage_tags:
                    if "下一页" in nextpage_tag.text:
                        nextpage_tag.click()
                        break
            except WebDriverException as e:
                logging.error("url: %s click issue: %s" % (_url, e))
                raise DaemonCrawlerClickError
            time.sleep(1)  # 点击完了之后睡眠一整秒也没有关系，一两秒都是加载不完的。
            if _url == self.browser.current_url:  # 点击之后页面没有跳转，说明 js 加载失误。
                break                             # 后续在对错误的 账号 进一步尝试。
            try:
                WebDriverWait(self.browser, self.timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-pager"))
                )
            except TimeoutException:  # 非第一页 load timeout，直接退出和 return
                break

        return page_sources


class DaemonCrawlerClickError(Exception):

    def __str__(self):
        return "daemonize_use_threadpool.py -> csdn -> un-Click-able"
