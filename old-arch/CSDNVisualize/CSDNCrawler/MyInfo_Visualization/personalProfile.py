#!/usr/bin/env python3

"""
# File Name: personalProfile.py
# Author   : Joseph Lin
# E-mail   : joseph.lin@aliyun.com
#

TODO:
  -[o] 重构两个类 - 使用字典
  -[o] UserData 得到的数据要适配准备给 django 的后台调用使用！
"""

import os, sys, io
from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import re
from time import sleep, ctime

from .attrdisplay import AttrDisplay

import multiprocessing

# 使用同级路径下的 phantojs/bin/ 文件夹下的 phantojs 应用程序作为默认
DEFAULT_BROWSER_PATH = './phantomjs/bin/'

if sys.platform == 'win32':
    DEFAULT_BROWSER_NAME = 'phantomjs.exe'
elif sys.platform == 'linux':
    DEFAULT_BROWSER_NAME = 'phantomjs'


class MyProcess(multiprocessing.Process):
    """docstring for MyProcess
    Reference: MyThread
    """

    def __init__(self, func, args, name='', doDebug=False):
        multiprocessing.Process.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.doDebug = doDebug

    def run(self):
        if self.doDebug: print('Starting ', self.name, 'at: ', ctime())
        # use multiprocessing.Manager() > manager.dict() to get return
        self.func(*self.args)
        if self.doDebug: print('Finished ', self.name, 'at: ', ctime())


# session = requests.Session()


def getSubTagfrom(tag, htmlId=None, htmlTag=None, htmlClass=None):
    subTag = None
    if htmlClass is not None:
        list_ = tag.findAll(htmlClass[0], {'class': htmlClass[1]})
        return list_[0]
    for content in tag.contents:
        """用 流畅的python 中的‘单分派泛函数’ 重构本段代码"""
        if htmlId is not None:
            key = htmlId
            '''因为 htmlclass 是后增加的，本段代码有点儿遗忘，
            所以把逻辑和之前的保持一致！'''
            if str(content).find(key) != -1:
                subTag = content
                break
        elif htmlTag is not None:
            key = htmlTag
            '''因为 htmlclass 是后增加的，本段代码有点儿遗忘，
            所以把逻辑和之前的保持一致！'''
            if str(content).find(key) != -1:
                subTag = content
                break
        else:
            break
    return subTag


def cover_WANG_to_integet(_str):
    highOrder = re.sub("\D", "", _str)
    if "万" in _str:
        return int(highOrder) * 10000 + 9999
    else:
        return int(highOrder)


class Page(object):
    def __init__(self, user_id,
                 browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME):
        self._id = user_id
        self.browser_path = browser_path


class BlogPage(Page):
    def __init__(self, user_id,
                 browser_path=DEFAULT_BROWSER_NAME + DEFAULT_BROWSER_NAME):
        super().__init__(user_id, browser_path)
        self.PERSONAL_BLOG_PAGE_URL = "https://blog.csdn.net/"

    def getBlogPageURL_by_UserID(self):
        return self.PERSONAL_BLOG_PAGE_URL + self._id

    def getBlogPageHTMLText(self):
        try:
            browser = webdriver.PhantomJS(executable_path=self.browser_path)
            browser.get(self.getBlogPageURL_by_UserID())
            sleep(2)
            pagesource = browser.page_source
        except WebDriverException as err:
            print("selenium > browser issue?：", err, file=sys.stderr)
            raise EnvironmentError  # sys.exit() 退出不合理,
        except Exception as err:
            print("产生异常：", err, file=sys.stderr)
            raise Exception         # 这样可能使调用该类的后台程序整个崩溃。
        finally:
            """ 因为预期 __del__ 会比 with 上下文管理器好实现，
            所以全部位置都使用 browser.close() 这样显示地调用。
              ^ 这段话是指我们未必每个像 PersonCSDN/PersonBlogCSDN 类
            在获取 page source 的时候，都需要调用一下 webdriver.<Browser>()
            我们应该可以使用一种更省资源的方法，在一个 views.func() 里面要
            获取网络数据的时候，共用一个 `browser`!
            我们可以考虑设计 instance_for_ONE_browser.close()
            或者 `del instance_for_ONE_browser`， 这样关闭 browser。
            """
            if 'browser' in locals():
                browser.close()
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
            dstKey = [ _char for _char in str(key) if _char not in ': \n\t：']
            dstValue = [ _char for _char in str(_dict[key]) if _char not in ': \n\t']
            dstKey = "".join(dstKey); dstValue = "".join(dstValue)
            dstDict[dstKey] = dstValue
        return dstDict

    def _setUserDataInfo(self, userDataInfoTag):
        userDataInfoDict = dict()
        for tagContent in userDataInfoTag.contents:
            if str(tagContent) == "\n": continue
            userDataInfoDict[tagContent.dt.string] = tagContent.dd.string

        self._articles = str(userDataInfoDict["原创"])
        self._beLiked  = str(userDataInfoDict["喜欢"])
        self._fans     = str(userDataInfoDict["粉丝"])
        self._beCommented = str(userDataInfoDict["评论"])

        if self._doDebug: print(userDataInfoDict, file=sys.stderr) 
        return True

    def _setUserGradeBox(self, userGradeBoxTag):
        userGradeBoxDict = dict()
        for tagContent in userGradeBoxTag.contents:
            if str(tagContent) == "\n": continue
            userGradeBoxDict[tagContent.dt.string] = tagContent.dd.string
        userGradeBoxDict = self._rmUneccessaryChar(userGradeBoxDict)

        self._rank = userGradeBoxDict["排名"]
        self._membPoints  = userGradeBoxDict["积分"]
        # self._fans     = userGradeBoxDict["等级"]
        self._beAccessed = userGradeBoxDict["访问"]
        return True

    def _setUserInformation(self):
        csdnHTMLData = self._hpHTMLData
        if self._doDebug: print("csdn blog home page: \n", csdnHTMLData, file=sys.stderr)
        try:
            csdnSoup = BeautifulSoup(csdnHTMLData, "html.parser")

            userAsideProfile = getSubTagfrom(csdnSoup.aside, htmlId="asideProfile")
            userDataInfo = getSubTagfrom(userAsideProfile, htmlId="data-info d-flex item-tiling")
            userGradeBox = getSubTagfrom(userAsideProfile, htmlId="grade-box clearfix")

            self._setUserDataInfo(userDataInfo)
            self._setUserGradeBox(userGradeBox)

        except Exception as e:
            print("_setUserInformation() function error!")
            print("Exception: ", e)
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
                sys.exit(1)

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
        try:
            browser = webdriver.PhantomJS(executable_path=self.browser_path)
            browser.get(self.getHomePageURL_by_UserID())
            for follow_tag in browser.find_elements_by_tag_name("span"):
                # if __debug__: print(follow_tag.text)
                if "关注" in follow_tag.text:
                    follow_tag.click()
                    break
            sleep(2)
            pagesource = browser.page_source
        except WebDriverException as err:
            print("selenium > browser issue?：", err, file=sys.stderr)
            raise EnvironmentError  # sys.exit() 退出不合理,
        except Exception as err:
            print("产生异常：", err, file=sys.stderr)
            raise Exception         # 这样可能使调用该类的后台程序整个崩溃。
        finally:
            if 'browser' in locals():
                browser.close()
        return pagesource


"""TODO:
 -[x] 根据 《Python 核心编程》 的 多线程使用方法（例18.7），
-[x] 重构 PersonCSDN
-[x] for user id of follows 重构 PersonCSDN
"""
class PersonCSDN(HomePage, AttrDisplay):
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
                print("PersonBlogCSDN> syncUserData> return_dict type ERROR!\n"
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
        self.user_homepage_data.syncUserData()
        self.user_blogpage_data.syncUserData()

        # 访问量；原创文章数量，转载数量；排名；评论量；点赞量；
        self._csdnc_bloglevel = self.user_homepage_data.csdnLevel
        self._beAccessed = self.user_homepage_data.beAccessed
        self._articles_number[0] = self.user_homepage_data.originality
        self._articles_number[1] = self.user_homepage_data.repeat
        self._rank = self.user_homepage_data.rank
        self._beCommented = self.user_homepage_data.beCommented
        self._beLiked = self.user_homepage_data.beLiked

        # membPoints, fans, follows
        self._fans = int(self.user_blogpage_data.fans)
        self._follows = int(self.user_blogpage_data.follows)
        self._membPoints = int(self.user_blogpage_data.membPoints)

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
                    if "fans_title" not in str(a_tag): continue
                    userfollowsDict[a_tag.string] = a_tag.attrs['href']

            # user id must have not '\n', ' ', '\t' etc...
            def clean_follows_userid_dict(dict_):
                for k, v in dict_.items():
                    del dict_[k]
                    k = k.replace('\n', '').replace(' ', '').replace('\r', '')
                    v = v.replace('\n', '').replace(' ', '').replace('\r', '')
                    # only user-id be needed, no need url:
                    dict_[k] = v.replace(self.PERSONAL_HOME_PAGE_URL, '')
                return dict_
            userfollowsDict = clean_follows_userid_dict(userfollowsDict)

            if __debug__:
                print("follows of %s:\n" % self._id, userfollowsDict, '\n')
            return userfollowsDict
        except Exception as err:
            print("SocialData> getFollows> error: ", err, file=sys.stderr)
            raise Exception


def getFollows_of_theUserID(user_id, browser_path=DEFAULT_BROWSER_PATH + DEFAULT_BROWSER_NAME):
    """
    -[x] 获取到的是粉丝列表，不是关注列表！！！
    """
    PERSONAL_HOME_PAGE_URL = "https://me.csdn.net/"
    try:
        # get user id home page source code
        # browser = webdriver.PhantomJS(executable_path=browser_path)
        browser = webdriver.Edge()
        browser.get(PERSONAL_HOME_PAGE_URL + user_id)
        follows = browser.find_elements_by_tag_name("span")
        for follow_tag in follows:
            # if __debug__: print(follow_tag.text)
            if "关注" in follow_tag.text:
                follow_tag.click()
                break
        sleep(1)
        pagesource = browser.page_source
        browser.close()

        # get data from home page source code
        csdnUserHPSoup = BeautifulSoup(pagesource, 'html.parser')

        userfollowsDict = dict()
        strictlyUserFollowsInfoTag = csdnUserHPSoup.find(
            lambda tag: "block" in str(tag),  # python 网络数据采集 & 2.6 !!!
            {'class': 'tab_page'}, )  # 并不确定 tag 使用函数之后，attributes 是否还有起到作用？

        for tagli in strictlyUserFollowsInfoTag.findAll('li'):
            for a_tag in tagli.findAll('a'):
                if "fans_title" not in str(a_tag): continue
                userfollowsDict[a_tag.string] = a_tag.attrs['href']

        def clean_follows_userid_dict(dict_):
            # user id must have not '\n', ' ', '\t', etc...
            for k, v in dict_.items():
                del dict_[k]
                k = k.replace('\n', '').replace(' ', '').replace('\r', '')
                v = v.replace('\n', '').replace(' ', '').replace('\r', '')
                # only user-id be needed, no need url:
                dict_[k] = v.replace(PERSONAL_HOME_PAGE_URL, '')
            return dict_
        userfollowsDict = clean_follows_userid_dict(userfollowsDict)

        if __debug__:
            print("follows of %s:\n" % user_id, userfollowsDict, '\n')
        return userfollowsDict
    except Exception as err:
        print("getFollows_of_theUserID > error: ", err, file=sys.stderr)
        raise Exception


def main(argc, argv):
    print("\nstart CSDN Data at time: ", ctime(), '\n')
    # USER_ID = "qq_29757283"
    USER_ID = "lizhe1985"
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
        else:
            print("only support multi/single")
    except IndexError as err:
        print("Usage: %s multi/single <phantomjs path>" % argv[0],
              file=sys.stderr)
        sys.exit(1)
    print("\nEnd CSDN Data at time: ", ctime(), '\n')

    sys.exit(0)


if __name__ == "__main__":
    if True:
        main(len(sys.argv), sys.argv)
    else:
        havePageSource = True
        try:
            # print(getFollows_of_theUserID(sys.argv[1], browser_path=sys.argv[2]))
            if havePageSource:
                csdn_homepage = HomePage(sys.argv[1], browser_path=sys.argv[2])
                pagesource = csdn_homepage.getHomePageHTMLText()
                # here is PersonCSDN handler.

                csdn_userid_socialData = SocialData(
                    sys.argv[1], pagesource=pagesource)
                print(csdn_userid_socialData.getFollows())
            else:
                csdn_userid_socialData = SocialData(sys.argv[1], browser_path=sys.argv[2])
                print(csdn_userid_socialData.getFollows())

        except IndexError:
            print("usage: %s <user id> <browser path>" % sys.argv[0], file=sys.stderr)
            sys.exit(1)
