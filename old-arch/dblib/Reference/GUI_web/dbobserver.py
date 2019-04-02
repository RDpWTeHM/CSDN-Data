"""dbobserver.py

"""

import os
import sys

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

from Crawl import Observer

from . import jobbole_userid_post
from . import jobbole_article_post
from sites.jobbole_com.db.dirtyjob import jobbole_userid_parse
from sites.jobbole_com.db.dirtyjob import jobbole_article_parse


class Observer_Jobbole_UserInfo(Observer):
    def __init__(self, user_id):
        self.user_id = user_id

    def notify(self, subject, *args, **kw):
        ''' get Subject instance is nessery,
          in case need Observer multi-subject,
          it can be used to distinguish.
        '''
        if subject:
            if __debug__:
                print("{} notify by:\n\t subject -> {}\n\t *args ->{}".format(
                      type(self).__name__, subject, args), file=sys.stderr)
            return self.db_create_userid(*args, **kw)

    def db_create_userid(self, *args, **kw):
        if __debug__:
            print("\n{}: notify> db_create_userid with:\n\t {!r} {!r}.".format(
                  type(self).__name__, args, kw),
                  file=sys.stderr)
        try:
            return jobbole_userid_post(jobbole_userid_parse(args[0]))
        except RuntimeError:
            raise


class ObserverJobboleArticle(Observer):
    def __init__(self, user_id):
        self.user_id = user_id

    def notify(self, subject, *args, **kw):
        ''' get Subject instance is nessery,
          in case need Observer multi-subject,
          it can be used to distinguish.
        '''
        if subject:
            if __debug__:
                print("{} notify by:\n\t subject -> {}\n\t *args ->{}".format(
                      type(self).__name__, subject, args), file=sys.stderr)
            args = args[1:]
            self.updateDB(*args, **kw)

    def updateDB(self, *args, **kw):
        # if __debug__:
        if True:
            print("\n{}: notify> updateDB with:\n\t {!r} {!r}.".format(
                  type(self).__name__, args, kw),
                  file=sys.stderr)
        try:
            print(
                jobbole_article_post(jobbole_article_parse(args[0], args[1])))
        except RuntimeError:
            raise
