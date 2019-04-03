# connection/crawl.py
"""

"""

# import os
import sys
import time
import traceback

try:
    from selenium import webdriver
    # from selenium.common.exceptions import WebDriverException

    from selenium.webdriver.common import desired_capabilities
except ImportError as exc:
    raise ImportError(
        "Couldn't import selenium. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc

from spider.website.csdn.userhome import UserInfoium


def get_crawl_csdn_userinfo(user_id, browser):
    userinfoium = UserInfoium(user_id, browser)
    return userinfoium.crawl()


def _create_new_browser():
    capa = desired_capabilities.DesiredCapabilities().CHROME
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
    _applewebkit_ver = [_V_537_36, _V_537_36, ]
    _chrome_ver = ["70.0.3538.102", "71.0.3578.98", ]
    _safari_ver = [_V_537_36, _V_537_36, ]

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


class Crawl():

    def __init__(self):
        self.__result = None
        self.browser = _create_new_browser()

    def execute(self, task):
        self.__result = get_crawl_csdn_userinfo(task, self.browser)

    def result(self):
        return self.__result

    def release(self):
        self.browser.quit()
