"""dblib/__init__.py

TODO: n/a
"""

import os
import sys

import json
import copy

import requests


URL_HEAD = "http://localhost:8010/"
URL_CSDNCRAWLER_API_HEAD = "api/v1/CSDNCrawler/"


class DRFOperate(object):
    permission = None  # -[o] not support for now
    headers = {"Content-Type": 'application/json'}

    def _gen_url(self,
                 user_id=None, visualdatas_idx=None,
                 fanses_idx=None, follows_idx=None):
        url = self.url
        if not user_id:
            return url
        elif user_id:
            idx = ""
            if not (visualdatas_idx or fanses_idx or follows_idx):
                return url + user_id + "/"
            elif visualdatas_idx:
                idx = str(visualdatas_idx) + "/"
            elif follows_idx:
                idx = str(follows_idx) + "/"
            elif fanses_idx:
                idx = str(fanses_idx) + "/"

            return url + user_id + "/" + idx

    def _handler_requests_result(self, r):
        return r.status_code, r.text


class DBUserID(DRFOperate):
    def __init__(self):
        self.url = URL_HEAD + URL_CSDNCRAWLER_API_HEAD + "userids/"

    def create(self, data):
        r = requests.post(self.url, json.dumps(data), headers=self.headers)
        return self._handler_requests_result(r)

    def update(self, data):
        r = requests.put(
            self._gen_url(data["user_id"]), json.dumps(data),
            headers=self.headers)
        return self._handler_requests_result(r)

    def retrieve(self, user_id):
        r = requests.get(self._gen_url(user_id))
        return self._handler_requests_result(r)


class DBVisualData(DRFOperate):
    pass


class DBFans(DRFOperate):
    pass


class DBFollow(DRFOperate):
    pass
