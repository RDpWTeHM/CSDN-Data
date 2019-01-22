"""fakeselenium.py
    for Test usage
"""
import sys
import os


class Browser(object):
    def __init__(self, *args, **kwargs):
        pass  # -[o] mapping self.*args = *args

    @property
    def text(self):
        print("{} run .text".format(type(self).__name__),
              file=sys.stderr)
        self._text = "{}._text".format(type(self).__name__)
        return self._text

    def get_attribute(self, *args, **kw):
        print("{} run .get_attribute():\n\t args > {} kw > {}".format(
            type(self).__name__, args, kw), file=sys.stderr)
        return "{}.get_attribute({}, {})".format(
            type(self).__name__, args, kw)

    def get(self, url):
        print("{} run get url:\n\t {}".format(type(self).__name__, url),
              file=sys.stderr)

    def find_element_by_xpath(self, xpath):
        print("{} run find element by xpath:\n\t {}".format(
            type(self).__name__, xpath), file=sys.stderr)
        return self


class Chrome(Browser):
    pass


class Edge(Browser):
    pass


class Firefox(Browser):
    pass
