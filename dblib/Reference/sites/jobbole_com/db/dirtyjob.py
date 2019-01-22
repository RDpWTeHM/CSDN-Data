
import os
import sys
import json
import re
import copy

import requests

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
from ..conf import jobbole_site_pk
from GUI.web import django_server_port


#
# utils
#
def cover2apiformat(site, datetime_str):
    if "jobbole" in site:
        return True  # -[o]


def jobbole_userid2pk(user_id):
    _url = "http://localhost:" + str(django_server_port) +\
           "/api/jobbole/userids/" + user_id + "/"
    r = requests.get(_url)
    _d = json.loads(r.text)
    pk = _d["id"]
    return pk


def jobbole_userid_parse(data):
    # fields = ("name", ~~"url"~~, "follow_num", "fan_num",
    #           "user_id", "regitster_date", "signature",
    #           "profession", "location", "powered_by")
    _d = copy.deepcopy(data)

    _url = _d.pop("url")
    _d["user_id"] = re.findall("http://www.jobbole.com/members/(.*)$", _url)[0]
    _d["powered_by"] = jobbole_site_pk
    # _d["regitster_date"] = cover2apiformat(_d.pop("regitster_date"))
    return json.dumps(_d)


def jobbole_article_parse(data, user_id):
    # fields = ("article_id", ~~"url"~~, "title",
    #           ~~"tag",~~
    #           "pub_date", "copyright",
    #           ~~"body",~~ ~~"res",~~
    #           "comment_num", "like_num", "collect_num",
    #           ~~"reputation_score", "from_user_id",~~ )
    _d = copy.deepcopy(data)
    _d["pub_date"] = '-'.join(
        [_ for _ in re.findall(r"^(\d{4})/(\d{2})/(\d{2})", _d.pop("pub_date"))[0]]
    ) + "T00:00:00Z"

    copyright = _d.pop("copyright")
    if "翻译" in copyright:
        _d["copyright"] = "translation"
        _d["from_user_id"] = jobbole_userid2pk(user_id)
    elif "出处" in copyright:
        _d["copyright"] = "reprint"
        _d["from_user_id"] = jobbole_userid2pk("jobbole_reprint")
    elif "专栏作者" in copyright:
        _d["copyright"] = "originality"
        _d["from_user_id"] = jobbole_userid2pk(user_id)
    else:
        print(copyright, file=sys.stderr)
        _d["copyright"] = "unknow"
        _d["from_user_id"] = jobbole_userid2pk("jobbole")

    for _t in ("comment_num", "like_num", "collect_num"):
        try:
            _d[_t] = int(re.findall(r"^(\d*)", _d[_t])[0])
        except ValueError:
            _d[_t] = 0

    # if __debug__:
    print("{!r}".format(_d), file=sys.stderr)

    return user_id, json.dumps(_d)
