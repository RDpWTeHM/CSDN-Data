"""observers.py

TODO:
  n/a
"""

import os
import sys

#
# Project path
#
"""
try:
    _cwd = os.getcwd()
    _proj_abs_path = _cwd[0:_cwd.find("super-spider")]  # not include super-spider
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
"""

from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def notify(self):
        """Subject call this func. """


class DBObserver(Observer):
    def notify(self, subject, *args, **kw):
        print("BDObserver> notify: ")
        print("\tsubject: {}".format(subject))
        print("\targs: \t(unpack status){}".format(args))
        print("\tkw: \t(unpack status){}".format(kw))
