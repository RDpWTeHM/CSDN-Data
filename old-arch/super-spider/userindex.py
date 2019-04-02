"""csdn_net/user/index.py

TODO:
  -[o] update to suit csdn
"""
import sys, os
from abc import ABC, abstractmethod

#
# Project path
#
''' no need when model at root-dir program
try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("super-spider")]
    if True:  # hole project as a package path
        _package_path = os.path.join(_proj_abs_path, "")
    else:
        _package_path = os.path.join(_proj_abs_path, "<package-dir>")

    if _package_path not in sys.path:
        sys.path.append(_package_path)

    # import <project packages>
except Exception:
    import traceback; traceback.print_exc();  # -[o] fix later by using argv
    sys.exit(1)
'''


################################
#  sites/csdn_net/__init__.py  #
################################
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


# from sites.jobbole_com import CommonVisitCrawl # /\ there it is!
# from GUI.web.selfupdating import update_jobbole_user_id_from_db

# from GUI.web import django_server_port


"""
class Subject_CSDN_UserInfo(CommonVisitCrawl, SubjectCrawl):
    def __init__(self, user_id, browser_type=None):
        CommonVisitCrawl.__init__(self)
        SubjectCrawl.__init__(self)
        self.user_id = user_id
        self.browser_type = browser_type

    def __str__(self):
        return "{}: {}".format(
            type(self).__name__, self.user_id)

    # -[o] check data define
    class data:
        # model = ...
        # -[o] update those \/
        fields = ("name", "url", "follow_num", "fan_num", )
        executions = {
            'name': {'xpath': "//div[@class='member-profile box']//span[@class='profile-title']//a",
                     'attribute': "text", },
            'url': {'xpath': "//div[@class='member-profile box']//span[@class='profile-title']//a",
                    'func': "get_attribute", 'vargs': ("href", ), },
            'follow_num': {'xpath': "//div[@class='profile-follow']/a",
                           'attribute': "text", },
            'fan_num': {'xpath': "//div[@class='profile-follow'][2]/a",
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
        # -[o] update those \/
        self.url = "http://www.jobbole.com/members/" + self.user_id + "/"
        return self.url

    def _monitor(self):
        SubjectCrawl._monitor(self, browser_type=self.browser_type)

    def run_update_from_db(self):
        print("you call {}@{} run_update_from_db".format(
            self.user_id, type(self).__name__
        ))
        # -[o] update this function! \/
        status_code, text = update_jobbole_user_id_from_db(self.user_id)
        # print("\nprint update_jobbole_user_id_from_db:", _)
        # print("[debug] ", )

        return status_code, text
"""


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

    """
    def run_update_from_db(self):
        print("you call {}@{} run_update_from_db".format(
            self.user_id, type(self).__name__
        ))
        # -[o] update this function! \/
        status_code, text = update_jobbole_user_id_from_db(self.user_id)
        # print("\nprint update_jobbole_user_id_from_db:", _)
        # print("[debug] ", )

        return status_code, text
    """
