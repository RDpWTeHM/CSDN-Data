"""__init__.py

"""

import os
import sys
import copy

import json
import requests
import re

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

#
# configuration
#
'''
-[o] hard-code here
'''
from sites.jobbole_com.conf import jobbole_site_pk
#                                       /\
# -[o] jobbole mapping pk not always the same


django_server_port = 9999


#
# utils
#
def gen_jobbole_userid_articles_api(user_id):
    return "http://localhost:" + str(django_server_port) +\
           "/api/jobbole/userids/" + user_id + "/articles/"


def gen_userids_api(site_pk):
    #              -[o] develop port \/
    return "http://localhost:" + str(django_server_port) +\
           "/api/sites/" + str(site_pk) + "/userids/"


def gen_userid_api(site_pk, user_id):
    return "http://localhost:" + str(django_server_port) +\
           "/api/sites/" + str(site_pk) +\
           "/userids/0/?id=" + user_id


api_headers = {'Content-Type': 'application/json', }


def requests_result_handler(r):
    if 200 <= r.status_code < 299:
        # print("\n============requests_result_handler======\n")
        # print(r.status_code, r.text)
        return r.status_code, r.text
    else:
        raise RuntimeError(r.status_code, r.text)


def post2(url, json_data):
    r = requests.post(url, headers=api_headers, data=json_data)
    return requests_result_handler(r)


def PUT2(url, json_data):
    r = requests.put(url, headers=api_headers, data=json_data)
    return requests_result_handler(r)


def jobbole_userid_post(json_data):
    url = gen_userids_api(jobbole_site_pk)
    return post2(url, json_data)


def jobbole_userid_update(user_id, json_data):
    url = gen_userid_api(jobbole_site_pk, user_id)
    return PUT2(url, json_data)


def jobbole_article_post(user_id_and_json_data):
    user_id, json_data = user_id_and_json_data
    url = gen_jobbole_userid_articles_api(user_id)
    return post2(url, json_data)
