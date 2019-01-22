"""sites/jobbole_com/schedule.py


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

import requests
import json

from .user.index import Subject_Joble_UserInfo
from .article.blog import Subject_Joble_UserArticle

#
# configuration
#
from .conf import jobbole_site_pk

from GUI.web import django_server_port

#
# utils
#
api_headers = {'Content-Type': 'application/json', }


def requests_result_handler(r):
    if 200 <= r.status_code < 299:
        return r.text
    else:
        raise RuntimeError(r.status_code, r.text)


jobbole_userid_monitor_dict = {}
jobbole_article_monitor_dict = {}

jobbole_userid_list_urlapi = "http://localhost:" + str(django_server_port) +\
                             "/api/sites/" + str(jobbole_site_pk) + "/userids/"

# -[o] not test yet
user_id_tmp = "dimple11"
jobbole_article_list_urlapi = "http://localhost:" + str(django_server_port) +\
                              "/api/jobbole/userids/" + user_id_tmp + "/articles/"


def setup():
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(10)
    pool.submit(setup_userids, )

    # for userid in userids:
    #     pool.submit(setup_articles, (userid, ))


def setup_userids():
    r = requests.get(jobbole_userid_list_urlapi)
    userids = json.loads(requests_result_handler(r))
    for userid in userids:
        user_id = userid["user_id"]
        jobbole_userid_monitor_dict[user_id] = Subject_Joble_UserInfo(user_id, "Chrome")


def setup_articles(user_id):
    r = requests.get(jobbole_article_list_urlapi)
    articles = json.loads(requests_result_handler(r))
    for article in articles:
        article = article["article_id"]
        jobbole_article_monitor_dict[article] = Subject_Joble_UserArticle(user_id, article, "Chrome")


def create_new_userid(user_id, observer):
    if jobbole_userid_monitor_dict.get(user_id, None):
        return "Exsit"
    subj = Subject_Joble_UserInfo(user_id, "Chrome")
    jobbole_userid_monitor_dict[user_id] = subj
    subj.register(observer)
    ret = (subj, (subj.create(observer)))
    return ret
