"""jobbole_com/article/blog.py

"""
import sys, os
# from abc import ABC, abstractmethod

#
# Project path
#
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

from Crawl import SubjectCrawl
# from Crawl import VisitCrawl

from sites.jobbole_com import CommonVisitCrawl


class Subject_Joble_UserArticle(CommonVisitCrawl, SubjectCrawl):
    def __init__(self, user_id, article_id, browser_type=None):
        CommonVisitCrawl.__init__(self)
        SubjectCrawl.__init__(self)
        self.user_id = user_id
        self.article_id = article_id
        self.browser_type = browser_type

    def __str__(self):
        return "{}: {}'s {}".format(
            type(self).__name__, self.user_id, self.article_id)

    class data:
        # model = ...
        fields = (
            "article_id",
            # "url",
            "title",
            # "tag",
            "pub_date", "copyright",
            # 'body',  # 'res',
            'comment_num', 'like_num', 'collect_num',
            # 'reputation_score',
            # from_user_id
        )
        executions = {
            "article_id": {'xpath': "//div[@class='post-adds']//span[1]",
                           'func': "get_attribute",
                           'vargs': ('data-post-id', ), },
            # 'url': {'xpath': "",
            #         'func': "get_attribute", 'vargs': ("href", ), },
            'title': {'xpath': "//div[@class='entry-header']/h1",
                      'attribute': "text", },
            # 'tag': {'xpath': "//div[@class='entry-meta']//p[@class='entry-meta-hide-on-mobile']//a[3]",
            #         'attribute': "text", },
            'pub_date': {'xpath': "//div[@class='entry-meta']//p[@class='entry-meta-hide-on-mobile']",
                         'attribute': "text", },
            'copyright': {
                'xpath': "//div[@class='entry']//div[@class='copyright-area']",
                'func': "get_attribute",
                'vargs': ('innerHTML', ), },
            # 'body': {'xpath': "//div[@class='entry']",
            #          'func': "get_attribute",
            #          'vargs': ('innerHTML', ), },
            'comment_num': {'xpath': "//div[@class='post-adds']/a/span",
                            'attribute': "text", },
            'like_num': {'xpath': "//div[@class='post-adds']//span[1]/h10",
                         'attribute': "text", },
            'collect_num': {'xpath': "//div[@class='post-adds']//span[2]",
                            'attribute': "text", },
            # 'reputation_score': {
            #      'xpath': "//div[@class='profile-follow'][2]/a",
            #              'attribute': "text", },
        }

    def _gen_url(self):
        self.url = "http://blog.jobbole.com/" + self.article_id + "/"
        return self.url

    def _monitor(self):
        self._setup_browser(browser_type=self.browser_type)
        self.notifyAll(self, self._parse(), self.user_id)

        self._free_browser()
