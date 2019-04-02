#!/usr/bin/env python3

"""
File Name   : webpage.py
Author      : Joseph Lin
E-mail      : joseph.lin@aliyun.com
Date        : 2018/Aug/26
Last Change : 2018/Nov/03

TODO:
  -[o] 重构类 - 使用字典
  -[o] import error warn
"""


import os
import sys
import io
from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# import re
from time import sleep
from time import ctime

from collections import OrderedDict

# this packege part
# from .attrdisplay import AttrDisplay
# from .concurrence import MyProcess
from .utils import getSubTagfrom, cover_WANG_to_integet
from .webpage import Page
# from .utils import DEFAULT_BROWSER_PATH, DEFAULT_BROWSER_NAME
from .utils import *

from .exceptions import *


class BlogPage(Page):
    def __init__(self, user_id,
                 browser_path=DEFAULT_BROWSER_NAME + DEFAULT_BROWSER_NAME):
        super().__init__(user_id, browser_path)
        self.PERSONAL_BLOG_PAGE_URL = "https://blog.csdn.net/"

    def getBlogPageURL_by_UserID(self):
        return self.PERSONAL_BLOG_PAGE_URL + self._id

    def getBlogPageHTMLText(self):
        # === negotiate the IPC port ===
        data = negotiateIPCInfo()

        IPCPort = data['port']
        """Use IPC, send mission to daemon
          which control the browser to get page source.
        """
        IPCData = {
            'port': IPCPort,
            'req_url': self.getBlogPageURL_by_UserID(),
        }
        del data, IPCPort
        pagesource = getPageSourceOf('BlogPage', IPCData)

        return pagesource


class PersonBlogCSDN(BlogPage):
    r"""personal CSDN information.
    request packages support:
        requests, BeautifulSoup4

    Usage::
        >>> myCSDNinfo = personCSDN("qq_29757283")

    2018/Aug/26 CSDN “博客”主页 结构！
      HTMLData = getHTMLText("https://blog.csdn.net/qq_29757283")
      csdnSoup = BeautifulSoup(HTMLData, "html.parser")
      +-----------+---------------------------------------------+
      |  文章列表  |    个人资料                                 |
      |   <main>  |    <aside>                                  | csdnSoup.
      |           |=============================================|   aside
      |           |<div id="asideProfile" class="aside-box">    | csdnSoup.
      |           |   ---------                                 | aside.div
      |           |  <div class="data-info d-flex item-tiling"> |
      |           |    原创   粉丝  喜欢  评论                   |
      |           |   ---------                                 |
      |           |  <div class="grade-box clearfix">           |
      |           |    等级  访问  积分  排名                    |
      |           |   -----------                               |
      |           |=============================================|
      |           |                                             |
      |           +---------------------------------------------+
      |                                                         |
      +---------------------------------------------------------+
    """

    def __init__(self, user_id, doDebug=False,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME,
                 pagesource=None):
        super().__init__(user_id, browser_path)
        self._hpHTMLData = pagesource
        ''' 所有文章 # 同级子类来处理文章data？
        ## list 内部是单独文章结构：
        ##    文章名，阅读量， 评论， 点赞， 日期，“属性（分类）”
        '''
        # self._articles = list()
        self._fans = 0              # 粉丝
        self._follows = -1          # 关注
        self._beLiked = 0           # 总 "喜欢"(点赞)
        self._beCommented = 0       # 总 “评论”
        self._beAccessed = 0        # 总访问量
        self._membPoints = 0        # CSDN 积分
        self._rank = 0              # 排名
        self._doDebug = doDebug
        if __debug__:  # 后期将会找时间，将所有使用 doDebug 的地方去除
            print("running PersonBlogCSDN __init__", file=sys.stderr)

    def __str__(self):
        _str = "user ID: {}\n".format(self._id)
        _str += "粉丝：{}\n点赞：{}\n评论：{}\n".format(
            self._fans, self._beLiked, self._beCommented)

        _str += "访问量：{}\n积分：{}\n排名：{}".format(
            self._beAccessed, self._membPoints, self._rank)
        return _str

    def _rmUneccessaryChar(self, _dict):
        dstDict = dict()
        for key in _dict.keys():
            dstKey = [_char for _char in str(key) if _char not in ': \n\t：']
            dstValue = [_char for _char in str(_dict[key]) if _char not in ': \n\t']
            dstKey = "".join(dstKey)
            dstValue = "".join(dstValue)
            dstDict[dstKey] = dstValue
        return dstDict

    def _setUserDataInfo(self, userDataInfoTag):
        userDataInfoDict = dict()
        for tagContent in userDataInfoTag.contents:
            if str(tagContent) == "\n":
                continue
            userDataInfoDict[tagContent.dt.string] = tagContent.dd.string

        self._articles = str(userDataInfoDict["原创"])
        self._beLiked = str(userDataInfoDict["喜欢"])
        self._fans = str(userDataInfoDict["粉丝"])
        self._beCommented = str(userDataInfoDict["评论"])

        if self._doDebug: print(userDataInfoDict, file=sys.stderr) 
        return True

    def _setUserGradeBox(self, userGradeBoxTag):
        userGradeBoxDict = dict()
        for tagContent in userGradeBoxTag.contents:
            if str(tagContent) == "\n":
                continue
            userGradeBoxDict[tagContent.dt.string] = tagContent.dd.string
        userGradeBoxDict = self._rmUneccessaryChar(userGradeBoxDict)

        self._rank = userGradeBoxDict["排名"]
        self._membPoints = userGradeBoxDict["积分"]
        # self._fans     = userGradeBoxDict["等级"]
        self._beAccessed = userGradeBoxDict["访问"]
        return True

    def _setUserInformation(self):
        csdnHTMLData = self._hpHTMLData
        if self._doDebug:
            print("csdn blog home page: \n", csdnHTMLData, file=sys.stderr)
        try:
            csdnSoup = BeautifulSoup(csdnHTMLData, "html.parser")

            userAsideProfile = getSubTagfrom(csdnSoup.aside, htmlId="asideProfile")
            userDataInfo = getSubTagfrom(userAsideProfile, htmlId="data-info d-flex item-tiling")
            userGradeBox = getSubTagfrom(userAsideProfile, htmlId="grade-box clearfix")

            self._setUserDataInfo(userDataInfo)
            self._setUserGradeBox(userGradeBox)

        except Exception as e:
            print("PersonBlogCSDN()> _setUserInformation() function error!")
            print("Exception: ", e)
            # print(csdnHTMLData, file=sys.stderr)
            sys.exit(-1)
        return True

    def _getMembPointsFromHTML(self):
        r""" get CSDN website member-points of User from User Home HTML Page.

            request packages:
                BeautifulSoup4
        :return: int
        """
        HTMLData = self._hpHTMLData
        membPoints = 0                  ## 积分

        return membPoints

    def syncUserData(self, return_dict=None):
        if self._hpHTMLData is None:  # 考虑使用装饰器自动化这段操作
            try:
                self._hpHTMLData = self.getBlogPageHTMLText()  # 继承父类方法
            except Exception:
                raise Exception
        else:
            pass
        self._setUserInformation()

        # support multiprocessing
        if return_dict is not None:
            # if isinstance(return_dict, dict):  # -[o] should be more precise!
            if True:  # -[o] 判断 return_dict 和 Manager().dict() 的方法还没有找到！
                """ 三则重构！
                -[o] 使用一个字典维护 "字符串", 和变量之间的关系
                    不！ 因为自己比较少用字典，所以倒是没有第一时间用！
                ！！ class 内这些变量最开始就应该使用字典！！
                """
                return_dict["fans"] = cover_WANG_to_integet(self._fans)
                return_dict["follows"] = self._follows
                return_dict['membPoints'] = cover_WANG_to_integet(self._membPoints)
            else:
                print("PersonBlogCSDN> syncUserData> return_dict type ERROR!\n"
                      "Forget usage multiprocessing.Manager().dict() ?",
                      file=sys.stderr)
                sys.exit(1)  # -[o] 直接整个退出应该不太合适！

    def __getattr__(self, attrname):
        if attrname == 'originality':
            print("WARNING: not achieve originality number yet!", file=sys.stderr)
            return -1  # 还未实现获取原创文章数量的代码。
        elif attrname == 'fans':        return cover_WANG_to_integet(self._fans)
        elif attrname == 'follows':     return self._follows
        elif attrname == 'beLiked':     return self._beLiked
        elif attrname == 'beCommented': return self._beCommented
        elif attrname == 'csdnLevel':
            print("WARNING: not achieve CSDN Level yet!", file=sys.stderr)
            return -1
        elif attrname == 'beAccessed':  return cover_WANG_to_integet(self._beAccessed)
        elif attrname == 'membPoints':  return cover_WANG_to_integet(self._membPoints)
        elif attrname == 'rank':        return cover_WANG_to_integet(self._rank)
        else:
            raise AttributeError


class PersonalArticles(BlogPage):
    r'''personal Articl data on CSDN
     {"artile id1": {"original": True, "title": "XXX", "pub_date": "",
                     "visit_num": 8, "comment_num": 0},
      "artile id2": {...}, }
        👆 一级数据，无法从 blog page 获取文章的点赞量。
    '''

    def __init__(self, user_id, doDebug=False,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME,
                 pagesources=None):
        '''page sources 代表一个 usr-id 发布了多篇文章，需要分页显示
             虽然一般如果要传递 page source 的话，也就只是第一页
        '''
        super().__init__(user_id, browser_path)
        self._articles = OrderedDict()  # 从外部 set articles 应该还是不合理的。
        self._bpHTMLsData = pagesources

    def __str__(self):
        _pasStr = "User-> %s's articles:\n" % self._id
        # do NOT clean data by mistake
        _articles = copy.deepcopy(self._articles)
        if any(_articles) is False:
            _pasStr += "{"
            for i in range(len(_articles.keys())):
                _id, _data = _articles.popitem(last=False)  # FIFO
                _pasStr += "\t\"" + _id + "\":" + str(_data)
            _pasStr += "}"
        else:
            _pasStr += "{\n}"

        return _pasStr

    def __getattr__(self, attrname):
        if attrname == "id":
            return self._id
        elif attrname == "articles":
            return self._articles
        else:
            raise IndexError

    def getBlogPageHTMLsText(self, firstPage=None):
        # -[x] joseph, IPC to recv page sources
        data = negotiateIPCInfo()
        IPCPort = data['port']
        IPCData = {
            'port': IPCPort,
            'req_url': self.getBlogPageURL_by_UserID(), }
        del data, IPCPort
        pagesources = getPageSourcesOf('ArticlesPages', IPCData)
        if pagesources == 'timeout':
            ''' 这里出现了一个动态类型的 case(应用场景) '''
            raise CrawlerTimeoutError
        elif pagesources == "Crawler Error":  # selenium 错误是应当考虑的。
            raise CrawlerError
        else:  # daemon 的该部分机制，并非第一个页面 timeout，就可以返回已经爬下来的页面
            pass

        self._bpHTMLsData = pagesources

    def _setArticlesInformation(self):
        for pagesource in self._bpHTMLsData:
            articleSoup = BeautifulSoup(pagesource, 'html.parser')
            articlesDivs = articleSoup.findAll(
                'div', {'class': 'article-item-box csdn-tracking-statistics'})
            for articleDiv in articlesDivs:
                articleid = articleDiv.attrs['data-articleid']
                originality = True if "原" in articleDiv.h4.a.span.string else False
                title = re.findall(r'</span>(.*)</a>',
                                   str(articleDiv.h4.a).replace('\n', '')
                                   )[0].strip().rstrip()
                pub_date = articleDiv.findAll('span', {'class': 'date'})[0].string
                read_num = -1; comment_num = -1
                for readnum in articleDiv.findAll('span', {'class': 'read-num'}):
                    if "阅读" in str(readnum):
                        read_num = re.findall(
                            r'阅读数(.*)</span>', str(readnum).replace("\n", '')
                            )[0].replace(":", '').replace("：", '').strip().rstrip()
                    elif '评论' in str(readnum):
                        comment_num = re.findall(
                            r'评论数(.*)</span>', str(readnum).replace("\n", '')
                            )[0].replace(":", '').replace("：", '').strip().rstrip()
                # like_num = -1  # 从这个页面无法获取
                self._articles[articleid] = {  # -[o] 使用获取本函数内的变量名方式重构本段代码
                    "originality": originality, 'title': title, 'pub_date': pub_date,
                    'read_num': read_num, 'comment_num': comment_num, }

    def syncArticlesData(self, return_dict=None):
        self.getBlogPageHTMLsText()

        self._setArticlesInformation()

        # support multiprocessing
        if return_dict is not None:
            # if isinstance(return_dict, dict):  # -[o] should be more precise!
            if True:  # -[o] 判断 return_dict 和 Manager().dict() 的方法还没有找到！
                return_dict['articles'] = self._articles
            else:
                print("PersonBlogCSDN> syncUserData> return_dict type ERROR!\n"
                      "Forget usage multiprocessing.Manager().dict() ?",
                      file=sys.stderr)
                sys.exit(1)  # -[o] 直接整个退出应该不太合适！
