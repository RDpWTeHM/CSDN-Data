#!/usr/bin/env python3

"""
File Name   : webpage.py
Author      : Joseph Lin
E-mail      : joseph.lin@aliyun.com
Date        : 2018/Oct/21
Last Change : 2018/Nov/03

Usage:
 PersonalData_v0.0.5/ $ python main.py


TODO:
  -[o] 重构类 - 使用字典
  -[x] UserData 得到的数据要适配准备给 django 的后台调用使用！
  -[x] 重构文件-构造包 之后的运行测试！
  -[o] import error warn
"""


import os, sys, io
from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# import re
from time import sleep, ctime

import multiprocessing

# this packege part
from .attrdisplay import AttrDisplay
from .concurrence import MyProcess
# from .utils import getSubTagfrom, cover_WANG_to_integet

from bs4 import BeautifulSoup
# from .utils import DEFAULT_BROWSER_PATH, DEFAULT_BROWSER_NAME
from .utils import *
'''-[o] import error alert
因为大概率使用“虚拟环境”的原因，
所以在没有使用虚拟环境的情况下， 需要提醒！
（就像 django 的 manage.py 那样！）
'''

from .exceptions import *

# session = requests.Session()


class Page(object):
    def __init__(self, user_id,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME):
        self._id = user_id
        self.browser_path = browser_path


class HomePage(Page):
    r"""personal CSDN information.
    request packages support:
        requests, BeautifulSoup4

    Usage::
        >>> myCSDNinfo = PersonCSDN("qq_29757283")

    2018/Aug/26 CSDN “个人”主页 结构！
      HTMLData = getHTMLText("https://me.csdn.net/<UserID>")
      csdnSoup = BeautifulSoup(HTMLData, "html.parser")
      +--------------------------------------------------------------+
      |__CSDN__博客__学院__下载__。。。。。____________________________|
      | ______________________________________[搜索框] 写博客 。。 ____|
      ||     >>博客<<   >>资源<<  >>帖子<<  >>问答<<    |   头像       |
      || 等级    访问   原创   转发    排名   评论  获赞 |   <网名>     |
      |+-----------------------------------------------+   [简介]     |
      ||  <最后一篇发表的博客标题>                       |             |
      || 阅读量                           <最后修改时间> |  行业信息    |
      |+-----------------------------------------------+    地标      |
      ||  <最近发表的博客。。。>                         |  奖章        |
      || 阅读量                           <最后修改时间> |>粉丝< >关注< |
      |+-----------------------------------------------+             |
      +--------------------------------------------------------------+
    """

    def __init__(self, user_id,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME):
        super().__init__(user_id, browser_path)
        self.PERSONAL_HOME_PAGE_URL = "https://me.csdn.net/"

    def getHomePageURL_by_UserID(self):
        return self.PERSONAL_HOME_PAGE_URL + self._id

    def getHomePageHTMLText(self):
        # === negotiate the IPC port ===
        data = negotiateIPCInfo()

        IPCPort = data['port']
        """Use IPC, send mission to daemon
          which control the browser to get page source.
        """
        IPCData = {'port': IPCPort,
                   'req_url': self.getHomePageURL_by_UserID()}
        del data, IPCPort
        pagesource = getPageSourceOf("HomePage", IPCData)
        return pagesource


class PersonCSDN(HomePage, AttrDisplay):
    """TODO:
     -[x] 根据 《Python 核心编程》 的 多线程使用方法（例18.7），
     -[x] 重构 PersonCSDN
     -[x] for user id of follows 重构 PersonCSDN
    """

    def __init__(self, userid, doDebug=False,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME,
                 pagesource=None):
        super().__init__(userid, browser_path)
        self._doDebug = doDebug
        self._hpHTMLData = pagesource      # Home Page HTML Data
        self._csdnc_bloglevel = -1         # CSDN 博客等级
        self._beAccessed = -1              # 总访问量
        self._articles_number = [-1, -1]   # 文章数量  # 固定两个值 - 原创，转发 考虑使用其它内置类型。
        """#  ~~list~~ 内部是单独文章结构：
           #   文章名，阅读量， 评论， 点赞， 日期，“属性（分类）”"""
        self._rank = -1                    # 排名
        self._beCommented = -1             # 总 “评论”
        self._beLiked = -1                 # 总 "喜欢"(点赞)
        """ 粉丝 - 关注 信息/数量 在侧边栏，和 blog 主页的集中 的信息有点儿不同"""
        # _fans = -1;  _follows = -1

    def _setUserInformation(self):
        if self._hpHTMLData == "timeout":  # timeout case!
            raise CrawlerTimeoutError
        try:
            csdnUserHPSoup = BeautifulSoup(self._hpHTMLData, 'html.parser')
            userBlogContent = getSubTagfrom(
                csdnUserHPSoup.body,
                htmlClass=('div', "tab_page my_tab_page"))
            # if doDebug: print(userBlogContent, file=sys.stderr)

            userDataInfoDict = dict()
            strictlyUserDataInfoTag = getSubTagfrom(
                userBlogContent,
                htmlClass=('ul', "mod_my_t clearfix"))
            for tagli in strictlyUserDataInfoTag.findAll('li'):
                userDataInfoDict[tagli.strong.string] = tagli.span.string
            # self._beAccessed = int(userDataInfoDict['等级'])
            self._beAccessed = int(userDataInfoDict['访问'])
            self._articles_number = (int(userDataInfoDict["原创"]),
                                     int(userDataInfoDict["转发"]))
            self._rank = int(userDataInfoDict['排名'])
            self._beCommented = int(userDataInfoDict["评论"])
            self._beLiked = int(userDataInfoDict["获赞"])
            if self._doDebug: print("userDataInfoDict: ", userDataInfoDict)
        except Exception as err:
            print("PersonCSDN class > _setUserInformation function ERROR!",
                  file=sys.stderr)
            print("Exception: ", err, file=sys.stderr)
            #sys.exit(os.EX_SOFTWARE)  # https://docs.python.org/3/library/os.html#os.EX_SOFTWARE
            sys.exit(1)

    def syncUserData(self, return_dict=None):
        if self._hpHTMLData is None:  # 考虑使用装饰器自动化这段操作
            try:
                self._hpHTMLData = super().getHomePageHTMLText()  # 父类方法
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
                return_dict['csdnLevel'] = -1
                return_dict['beAccessed'] = self._beAccessed
                return_dict["originality"] = self._articles_number[0]
                return_dict["repeat"] = self._articles_number[1]
                return_dict['rank'] = self._rank
                return_dict['beLiked'] = self._beLiked
                return_dict['beCommented'] = self._beCommented

            else:
                print("PersonCSDN> syncUserData> return_dict type ERROR!\n"
                      "Forget usage multiprocessing.Manager().dict() ?",
                      file=sys.stderr)
                sys.exit(1)

    def __str__(self):
        _str = "user ID: {}\n".format(self._id)
        _str += "等级：{}\n原创：{}\n转发：{}\n".format(
            None, self._articles_number[0], self._articles_number[1], )

        _str += "访问量：{}\n排名：{}\n".format(
            self._beAccessed, self._rank, )

        _str += "总获赞：{}\n总评论：{}\n".format(
            self._beLiked, self._beCommented, )
        """
        _str += "积分：{}\n粉丝：{}\n关注：{}".format(
            self._membPoints, self._fans, self._follows)
        """
        return _str

    def __getattr__(self, attrname):
        if attrname == 'originality':   return self._articles_number[0]
        elif attrname == 'repeat':      return self._articles_number[1]
        # elif attrname == 'fans':        return self._fans  # fans number support by PersonBlog for now
        # elif attrname == 'follows':      return self._follows  # follows number support by PersonBlog for now
        elif attrname == 'beLiked':     return self._beLiked
        elif attrname == 'beCommented': return self._beCommented
        elif attrname == 'csdnLevel':
            print("WARNING: not achieve CSDN Level yet!", file=sys.stderr)
            return -1
        elif attrname == 'beAccessed': return self._beAccessed
        elif attrname == 'membPoints': return self._membPoints
        elif attrname == 'rank':       return self._rank
        else: raise AttributeError


from .blogpage import PersonBlogCSDN


class UserData():
    _csdnc_bloglevel = -1         # CSDN 博客等级
    _beAccessed = -1              # 总访问量
    _articles_number = [-1, -1]   # 文章数量  # 固定两个值 - 原创，转发 考虑使用其它内置类型。
    """#  ~~list~~ 内部是单独文章结构：
       #   文章名，阅读量， 评论， 点赞， 日期，“属性（分类）”"""
    _rank = -1                    # 排名
    _beCommented = -1             # 总 “评论”
    _beLiked = -1                 # 总 "喜欢"(点赞)
    """ 粉丝 - 关注 信息/数量 在侧边栏，
    和 blog 的集中 的信息有点儿不同，需要和 积分一样适当适应一下。"""
    _fans = -1                    # 粉丝
    _follows = -1                 # 关注
    """ 目前看来，积分在“个人主页”上无法获取；
    积分这一项.... -[x] 单独写个从 blog 主页获取它的值的 function。"""
    _membPoints = -1               # CSDN 积分

    def __init__(self, userid, doDebug=False,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME,
                 home_pagesource=None, blog_pagesource=None):
        self._id = userid
        self.doDebug = doDebug
        self.user_homepage_data = PersonCSDN(
            self._id, browser_path=browser_path, pagesource=home_pagesource)
        self.user_blogpage_data = PersonBlogCSDN(
            self._id, browser_path=browser_path, pagesource=blog_pagesource)

    def __getattr__(self, attrname):
        if attrname == 'originality':   return self._articles_number[0]
        elif attrname == 'repeat':      return self._articles_number[1]
        elif attrname == 'fans':        return self._fans
        elif attrname == 'follows':     return self._follows
        elif attrname == 'beLiked':     return self._beLiked
        elif attrname == 'beCommented': return self._beCommented
        elif attrname == 'csdnLevel':
            print("WARNING: not achieve CSDN Level yet!", file=sys.stderr)
            return -1
        elif attrname == 'beAccessed': return self._beAccessed
        elif attrname == 'membPoints': return self._membPoints
        elif attrname == 'rank':       return self._rank
        else: raise AttributeError

    def __str__(self):
        _str = "user ID: {}\n".format(self._id)
        _str += "等级：{}\n原创：{}\n转发：{}\n".format(
            None, self._articles_number[0], self._articles_number[1], )

        _str += "访问量：{}\n排名：{}\n".format(
            self._beAccessed, self._rank, )

        _str += "总获赞：{}\n总评论：{}\n".format(
            self._beLiked, self._beCommented, )

        _str += "积分：{}\n粉丝：{}\n关注：{}".format(
            self._membPoints, self._fans, self._follows)
        return _str

    def syncCSDNData(self):
        try:
            self.user_homepage_data.syncUserData()

            # 访问量；原创文章数量，转载数量；排名；评论量；点赞量；
            self._csdnc_bloglevel = self.user_homepage_data.csdnLevel
            self._beAccessed = self.user_homepage_data.beAccessed
            self._articles_number[0] = self.user_homepage_data.originality
            self._articles_number[1] = self.user_homepage_data.repeat
            self._rank = self.user_homepage_data.rank
            self._beCommented = self.user_homepage_data.beCommented
            self._beLiked = self.user_homepage_data.beLiked
        except CrawlerTimeoutError:
            pass

        try:
            self.user_blogpage_data.syncUserData()

            # membPoints, fans, follows
            self._fans = int(self.user_blogpage_data.fans)
            self._follows = int(self.user_blogpage_data.follows)
            self._membPoints = int(self.user_blogpage_data.membPoints)
        except CrawlerTimeoutError:
            pass

    def quikSyncCSDNData(self):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        hp_pro = MyProcess(self.user_homepage_data.syncUserData,
                           (return_dict, ), "User Home Page", doDebug=True)
        bp_pro = MyProcess(self.user_blogpage_data.syncUserData,
                           (return_dict, ), "User Blog Page", doDebug=True)
        hp_pro.start()
        bp_pro.start()

        hp_pro.join()
        bp_pro.join()

        return return_dict


class SocialData(HomePage):
    def __init__(self, user_id,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME,
                 pagesource=None):
        super().__init__(user_id, browser_path)
        self.pagesource = pagesource

    def getFollows(self):
        if self.pagesource is None:  # 考虑使用装饰器自动化这段操作
            try:
                self.pagesource = super().getHomePageHTMLText()  # 父类方法
            except Exception:
                import traceback; traceback.print_exc();
                raise Exception
        else:
            pass
        try:
            # get data from home page source code
            csdnUserHPSoup = BeautifulSoup(self.pagesource, 'html.parser')

            userfollowsDict = dict()
            strictlyUserFollowsInfoTag = csdnUserHPSoup.find(
                lambda tag: "block" in str(tag),  # python 网络数据采集 & 2.6 !!!
                {'class': 'tab_page'})  # 并不确定 tag 使用函数之后，attributes 是否还有起到作用？

            for tagli in strictlyUserFollowsInfoTag.findAll('li'):
                for a_tag in tagli.findAll('a'):
                    if "fans_title" not in str(a_tag):
                        continue
                    userfollowsDict[a_tag.string] = a_tag.attrs['href']

            # if __debug__:
            #     print("\nfollows of %s:\nbefore clean data\n" % self._id,
            #           userfollowsDict, '\n', file=sys.stderr)

            # user id must have not '\n', ' ', '\t' etc...
            def clean_follows_userid_dict(tuple_kv_list):
                dict_ = {}
                for k, v in tuple_kv_list:
                    k = k.replace('\n', '').replace(' ', '').replace('\r', '')
                    v = v.replace('\n', '').replace(' ', '').replace('\r', '')
                    # only user-id be needed, no need url:
                    dict_[k] = v.replace(self.PERSONAL_HOME_PAGE_URL, '')
                return dict_

            _ = [(k, v) for k, v in userfollowsDict.items()]
            userfollowsDict = clean_follows_userid_dict(_)

            # if __debug__:
            #     print("\nfollows of %s:\nafter clean data\n" % self._id,
            #           userfollowsDict, '\n', file=sys.stderr)
            return userfollowsDict
        except Exception as err:
            print("SocialData> getFollows> error: ", err, file=sys.stderr)
            raise Exception
