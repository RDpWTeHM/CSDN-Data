"""GUI/web/selfupdating.py


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

from . import gen_jobbole_userid_articles_api
from . import jobbole_userid_update
from sites.jobbole_com.conf import jobbole_site_pk


def update_jobbole_user_id_from_db(user_id):
    dbapiurl = gen_jobbole_userid_articles_api(user_id)
    r = requests.get(dbapiurl)
    if r.status_code != 200:
        raise RuntimeError(r.status_code, r.text)

    articles = json.loads(r.text)
    # fields = ("name", ~~"url"~~, "follow_num", "fan_num",
    #           "user_id", "regitster_date", "signature",
    #           "profession", "location", "powered_by")
    update_fields = ("like_num", "comment_num", )
    model_d = {"article_num": len(articles)}

    for field in update_fields:
        model_d[field] = 0  # -[o] take care -1 case!
    for article_info in articles:
        for field in update_fields:
            model_d[field] += article_info[field]

    # -[o] update later, api had been specific site and user_id,
    # so, there is no need.
    model_d["powered_by"] = jobbole_site_pk
    model_d["user_id"] = user_id

    status_code, text = jobbole_userid_update(user_id, json.dumps(model_d))

    # yield status_code, text
    return status_code, text
