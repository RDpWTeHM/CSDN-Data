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

from personalProfile import PersonCSDN, UserData

doDebug = True
# doDebug = False



def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        if r.encoding != r.apparent_encoding:
            r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def main(argc, argv):
    print("start download image at time: ", ctime())
    # htmlData = getHTMLText("https://blog.csdn.net/qq_29757283")
    # myCSDNInfo = PersonCSDN("qq_29757283", doDebug=True)
    # myCSDNInfo.syncUserData()
    myCSDNInfo = UserData("qq_29757283", doDebug=True)
    myCSDNInfo.syncCSDNData()
    print(myCSDNInfo)
    print("End download image at time: ", ctime())

    sys.exit(0)


if __name__ == "__main__":
    print("\n>>>> I AM main.py <<<<<<<\n", file=sys.stderr)
    print("!!! from now on, DO NOT USE ME TO DO TEST!!!!", file=sys.stderr)
    main(len(sys.argv), sys.argv)

