"""csdn_net/user/index.py

TODO:
  -[x] update to suit csdn
"""
import sys
# import os
from time import sleep
import traceback
from abc import ABC, abstractmethod


class crawlium(ABC):
    """TODO: 需要改写成元类，检查 self.data，self.browser 继承创建"""

    def factory_execute_attrname(self, attrname, *args, **kw):
        methname = 'execute_' + type(attrname).__name__
        meth = getattr(self, methname, None)
        if meth is None:
            return self.generic_factory_execute_attrname(attrname, *args, **kw)
        return meth(*args, **kw)

    #
    # metaclasses to check "class data" exsit?
    #
    def _parse(self):
        d = {}
        for attr in self.data.fields:
            d[attr] = self.factory_execute_attrname(attr)
        return d

    @abstractmethod
    def _gen_url(self):
        pass

    def generic_factory_execute_attrname(self, attrname):
        try:
            elem = self.browser.find_element_by_xpath(
                self.data.executions[attrname]['xpath'])
            if "attribute" in self.data.executions[attrname].keys():
                ret = getattr(elem,
                              self.data.executions[attrname]['attribute'])
            elif "func" in self.data.executions[attrname].keys():
                func = getattr(elem, self.data.executions[attrname]['func'])
                ret = func(*self.data.executions[attrname]['vargs'])
        except Exception:
            print("Error when execute_attrname: {}".format(attrname),
                  file=sys.stderr)
            traceback.print_exc()
            raise
        return ret

    def crawl(self):
        try:
            self.browser.get(self._gen_url())
            # if element is OK
            sleep(3)
            return self._parse()
        except Exception:
            traceback.print_exc()
            raise


class UserInfoium(crawlium):
    def __init__(self, user_id, browserconn):
        self.user_id = user_id
        self.browser = browserconn

    def __str__(self):
        return "{}: {}".format(type(self).__name__, self.user_id)

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

    def _gen_url(self):
        self.url = "https://me.csdn.net/" + self.user_id
        return self.url

    def crawl(self):
        try:
            self.browser.get(self._gen_url())
            # if element is OK
            sleep(3)
            d = self._parse()
            for k, v in d.items():
                try:
                    d[k] = int(v)
                except ValueError:
                    pass
            return d
        except Exception:
            traceback.print_exc()
            raise
