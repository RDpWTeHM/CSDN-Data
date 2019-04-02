#!/usr/bin/env python3

"""
# File Name: main.py
# Author   : Joseph Lin
# E-mail   : joseph.lin@aliyun.com
#
###
###
###
"""


import os, sys, io

import bs4
from bs4 import BeautifulSoup
import requests
from time import sleep, ctime


doDebug = True
# doDebug = False


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        if r.encoding != r.apparent_encoding:
            r.encoding = r.apparent_encoding
        return r.text
    except Exception:
        return "产生异常"



from PersonalData.webpage import UserData
from PersonalData.webpage import SocialData
from PersonalData.blogpage import PersonalArticles
from PersonalData.utils import *

from PersonalData.exceptions import *


def main(argc, argv):
    print("\nstart CSDN Data at time: ", ctime(), '\n')
    # USER_ID = "qq_29757283"
    # USER_ID = "lizhe1985"
    USER_ID = "valada"
    try:
        if argv[1] == 'single':  # single processing
            # 回归测试！
            myCSDNInfo = UserData(USER_ID, doDebug=True,
                                  browser_path=argv[2])
            myCSDNInfo.syncCSDNData()
            print(myCSDNInfo)
        elif argv[1] == 'multi':
            if False:
                csdn_homepage = HomePage(USER_ID, browser_path=sys.argv[2])
                home_pagesource = csdn_homepage.getHomePageHTMLText()

                csdn_blogpage = BlogPage(USER_ID, browser_path=sys.argv[2])
                blog_pagesource = csdn_blogpage.getBlogPageHTMLText()
                myCSDNInfo = UserData(USER_ID, doDebug=False,
                                      home_pagesource=home_pagesource,
                                      blog_pagesource=blog_pagesource)
            else:
                myCSDNInfo = UserData(USER_ID, doDebug=True,
                                      browser_path=argv[2])
            dict_ = myCSDNInfo.quikSyncCSDNData()
            print(dict_)

        elif argv[1] == 'SocialData':
            csdn_userid_socialData = SocialData(
                "qq_29757283", browser_path=argv[2])
            print(csdn_userid_socialData.getFollows())
        elif argv[1] == 'Articles':
            csdn_userid_articles = PersonalArticles(
                'jinjianghai', browser_path=argv[2])
                # 'lizhe1985', browser_path=argv[2])
            try:
                csdn_userid_articles.syncArticlesData()
            except CrawlerTimeoutError:
                print("Crawler Articles Connection CSDN timeout!")
                sys.exit(1)
            articles = csdn_userid_articles.articles
            print(articles)
            if __debug__:  # just for test ordereddict usage
                # for i, (k, v) in enumerate(articles.items()):  # this could work
                i = 0
                for k, v in articles.items():  # this could work too
                    i = i + 1
                    print("=" * 15, "  {}  ".format(i), "=" * 15)
                    print("article id: ", k)
                    print("\toriginality: ", v['originality'])
                    print("\ttitle: ", v['title'])
                    print("\tpublish DateTime: ", v['pub_date'])
                    print('\treaded number: ', v['read_num'])
                    print('\tcommented number: ', v['comment_num'])
        else:
            print("only support multi/single/SocialData/Articles")
    except IndexError as err:
        print("Usage: %s multi/single/SocialData/Articles <phantomjs path>" % argv[0],
              file=sys.stderr)
        sys.exit(1)
    print("\nEnd CSDN Data at time: ", ctime(), '\n')

    sys.exit(0)


if __name__ == "__main__":
    print("\n>>>> I AM main.py <<<<<<<", file=sys.stderr)
    print("Develop test by running me....\n", file=sys.stderr)
    main(len(sys.argv), sys.argv)
