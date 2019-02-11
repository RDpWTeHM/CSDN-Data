"""csdn_net/user/index.py

TODO:
  n/a

Usage:
  (CSDN-Data) .../crawllib/tests $ python -O 20190211_CSDN_UserIndex_Reference.py
"""
import sys, os

#
# Project path
# -[o] no need at TestCase #########################
#
try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("super-spider")]  # stop before super-sipder
    if True:  # hole project as a package path
        _package_path = os.path.join(_proj_abs_path, "super-spider")
    else:
        _package_path = os.path.join(_proj_abs_path, "<package-dir>")

    if _package_path not in sys.path:
        sys.path.append(_package_path)

    # import <project packages>
except Exception:
    import traceback; traceback.print_exc();  # -[o] fix later by using argv
    sys.exit(1)
else:
    print("{}\n".format(sys.path))


from abc import ABC, abstractmethod
################################
#  sites/csdn_net/__init__.py  #
################################
# -[o] update to TestCase
from crawllib import SubjectCrawl
from crawllib import VisitCrawl


class CommonVisitCrawl(VisitCrawl, ABC):
    def __init__(self):
        VisitCrawl.__init__(self)

    def _setup_browser(self, browser_type=None):
        VisitCrawl._setup_browser(self, browser_type=None)

    def _free_browser(self):
        VisitCrawl._free_browser(self)

    @abstractmethod
    def _gen_url(self):
        pass


class Subject_CSDN_UserInfoVisual(CommonVisitCrawl, SubjectCrawl):
    def __init__(self, user_id, browser_type=None):
        CommonVisitCrawl.__init__(self)
        SubjectCrawl.__init__(self)
        self.user_id = user_id
        self.browser_type = browser_type

    def __str__(self):
        return "{}: {}".format(
            type(self).__name__, self.user_id)

    class data:
        # model = ...
        fields = ("originality", "reprint",
                  "fans", "follow", "likes", "comments",
                  # "csdnlevel",
                  "visitors",
                  # "intergration",
                  "rank", )
        executions = {
            'originality': {'xpath': "//div[@class='tab_page my_tab_page']/ul[@class='mod_my_t clearfix']//li[3]/span",
                            'attribute': "text", },
            'reprint': {'xpath': "//div[@class='tab_page my_tab_page']/ul[@class='mod_my_t clearfix']//li[4]/span",
                        'attribute': "text", },
            # 'func': "get_attribute", 'vargs': ("href", ), },
            'fans': {'xpath': "//div[@class='my_fans js_fans_att clearfix']/ul[@class='my_fans_bar']//li[1]/em",
                     'attribute': "text", },
            'follow': {'xpath': "//div[@class='my_fans js_fans_att clearfix']/ul[@class='my_fans_bar']//li[2]/em",
                       'attribute': "text", },
            'likes': {'xpath': "//div[@class='tab_page my_tab_page']/ul[@class='mod_my_t clearfix']//li[7]/span",
                      'attribute': "text", },
            'comments': {'xpath': "//div[@class='tab_page my_tab_page']/ul[@class='mod_my_t clearfix']//li[6]/span",
                         'attribute': "text", },
            'visitors': {'xpath': "//div[@class='tab_page my_tab_page']/ul[@class='mod_my_t clearfix']//li[2]/span",
                         'attribute': "text", },
            'rank': {'xpath': "//div[@class='tab_page my_tab_page']/ul[@class='mod_my_t clearfix']//li[5]/span",
                     'attribute': "text", },
        }

    def execute_name(self):
        elem = self.browser.find_element_by_xpath(
            self.data.executions['name']['xpath'])
        if "attribute" in self.data.executions['name'].keys():
            ret = getattr(elem, self.data.executions['name']['attribute'])
        elif "func" in self.data.executions['name'].keys():
            func = getattr(elem, self.data.executions['name']['func'])
            ret = func(*self.data.executions['name']['vargs'])
        return ret

    def _gen_url(self):
        self.url = "https://me.csdn.net/" + self.user_id
        return self.url

    def _monitor(self):
        SubjectCrawl._monitor(self, browser_type=self.browser_type)


# -[o] update to TestCase
from crawllib import Observer


class DBObserver(Observer):
    def notify(self, *args, **kw):
        print("BDObserver> notify: *args: {}\n\t**kw: {}".format(
            *args, **kw))


################################################
# -[o] Reference here, Update to TestCase      #
################################################
def main():
    observer = DBObserver()
    sub = Subject_CSDN_UserInfoVisual('qq_29757283', "Chrome")
    sub.register(observer)
    sub.run()


if __name__ == '__main__':
    main()
