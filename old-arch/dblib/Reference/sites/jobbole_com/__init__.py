"""jobbole_com/__init__.py

"""
import sys, os
from abc import ABC, abstractmethod

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
from Crawl import VisitCrawl


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
