#!/usr/bin/env python3

"""
# filename: runCSDNCrawler.py
# function: 访问站点来启动爬虫
"""


import sys
# import os

argc = len(sys.argv)
if argc < 2:
    print("Usage: %s <SERVER IP/Domain> [USER ID]" % sys.argv[0],
          file=sys.stderr)
    sys.exit(1)

try:
    startcrawlerurl = 'http://%s:8000/CSDNCrawler/startcrawler/?user_id=%s' % (
        sys.argv[1], sys.argv[2])
except IndexError:
    startcrawlerurl = 'http://%s:8000/CSDNCrawler/startcrawler/' % sys.argv[1]


from time import sleep
from selenium import webdriver
# from collections import joseph
from bs4 import BeautifulSoup
import requests
from random import randint


def get_new_missions(pagesource):
    missions_dict = {}
    bs = BeautifulSoup(pagesource, "html.parser")
    for each_tr in bs.findAll('tr'):
        try:
            webname = each_tr.strong.string.replace(":", '').replace(" ", '')
            missions_dict[webname] = each_tr.i.string
        except AttributeError as err:  # each_tr has no strong: th case
            if __debug__:
                print("get_new_missions> AttributeError: ", err, file=sys.stderr)
    if __debug__:
        print("\nget_new_missions: \n", missions_dict, "\n", file=sys.stderr)
    return missions_dict


def main():
    """ 使用 $ python -O <server addr> <start id> 运行
    """
    mission = ('', sys.argv[2])
    try:
        if __debug__:
            # browser = webdriver.Edge()
            browser = webdriver.Firefox()

        crawlerurl = startcrawlerurl
        while True:
            if __debug__:
                browser.get(crawlerurl)
                # browser.implicite.wait(1)

                assert 'CSDN Personal Profile Crawler' in browser.title
            else:
                r = requests.get(crawlerurl, timeout=120)
                if r.status_code == 500:
                    """出现了没有发表过文章的用户id，不存在 blog 首页，
                    请求 blog 首页倒是不会失败，因为是 404 的页面， bs4 解析的时候，
                    会 raise content 错误。然后从该实例获取值会有问题，会在 django
                    那边 暂时先绕过。 但是可能还会有其它问题，所以这里仍然还是要判断一下
                    """
                    crawlerurl = 'http://%s:8000/CSDNCrawler/startcrawler/?user_id=%s' % (
                        sys.argv[1], "qq_29757283")
                    continue
                if r.encoding != r.apparent_encoding:
                    r.encoding = r.apparent_encoding

            # get new mission from browser.page_source
            if __debug__:
                missions_dict = get_new_missions(browser.page_source)
            else:
                missions_dict = get_new_missions(r.text)
            # >> missions
            # .popitem() django 那边没有 new mission 了， 退出程序，没毛病。
            webname, user_id = missions_dict.popitem()
            mission = (webname, user_id)
            crawlerurl = 'http://%s:8000/CSDNCrawler/startcrawler/?user_id=%s' % (
                sys.argv[1], mission[1])
            sleep(randint(2, 9))
    except Exception as err:
        print("Some Error?\n", file=sys.stderr)
        print("Exception: ", err, file=sys.stderr)
    finally:
        if "browser" in locals():
            browser.close()


if __name__ == "__main__":
    main()
