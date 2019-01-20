"""dblib/__init__.py

TODO: n/a
"""

import os
import sys
from collections import OrderedDict

import json
import copy

import requests


URL_HEAD = "http://localhost:8010/"
URL_CSDNCRAWLER_API_HEAD = "api/v1/CSDNCrawler/"


class DRFOperate(object):
    '''
    TODO:
       -[o] create, retrieve, update, ... response dict -> self.data
       ------
       -[o] __getattr__ => `.<the item>` -mapping-> self.data["<the item>"]
    '''

    permission = None  # -[o] not support for now
    headers = {"Content-Type": 'application/json'}
    url = URL_HEAD + URL_CSDNCRAWLER_API_HEAD + "userids/"
    head_url = URL_HEAD + URL_CSDNCRAWLER_API_HEAD

    def _handler_requests_result(self, r):
        return r.status_code, r.text

    def get_url(self, detail, kw_belong=None, ):
        if kw_belong and not isinstance(kw_belong, OrderedDict):
            raise ValueError("Please use OrderedDict for generate url")

        try:
            belong_url = self.head_url
            if kw_belong:
                '''{"sites": 'www_csdn_net', "user_ids": 'heheda', }
                '''
                for _ in range(len(kw_belong)):
                    k, v = kw_belong.popitem(last=False)
                    belong_url += k + '/' + v + '/'

            if isinstance(detail, str):
                return belong_url + detail + "/"
            elif isinstance(detail, tuple):
                return belong_url + detail[0] + "/" + "{}".format(detail[1]) + "/"
            else:
                raise ValueError("Please use correct 'detail' type.")
        except ValueError:
            raise
        except Exception as err:
            print(err, file=sys.stderr)
            raise

    def create(self, data):
        r = requests.post(self.get_url(self.api_be[0], self.api_kw_belong),
                          json.dumps(data), headers=self.headers)
        return self._handler_requests_result(r)

    def update(self, data):
        r = requests.put(
            self.get_url(self.api_be, self.api_kw_belong),
            json.dumps(data),
            headers=self.headers)
        return self._handler_requests_result(r)

    def retrieve(self, index=True):
        if index is True and self.api_be[1]:  # retrieve obj's detail
            r = requests.get(
                self.get_url(self.api_be, self.api_kw_belong))
        elif index and index is not True:  # retrieve specific detail
            r = requests.get(
                self.get_url((self.api_be[0], index), self.api_kw_belong))
        elif index is False or not self.api_be[1]:  # retrieve list
            r = requests.get(
                self.get_url(self.api_be[0], self.api_kw_belong))
        else:
            raise ValueError(
                "unexpect 'index': {}@{}".format(type(index), index))
        return self._handler_requests_result(r)


class DBUserID(DRFOperate):
    '''
    demo:
        obj = DBUserID("qq_29757283") =>
            api_be <- ("userids", user_id)
            api_kw_belong <- None

        obj = DBUserID() =>
            api_be <- ('userids', None)
            api_kw_belong <- None

    Note: `.read` 100% open to be used

    TODO:
       -[o] Metaclass to fobidden `.update`
            if using like DBUserID().update(user_id, update_d)
       -[o] Metaclass to fobidden `.create`
            if using like DBUserID(<user_id>).create(dict(<the same user_id>)) (if exist)
            -[o] add method to check the instance user_id in DB or not!
            (DBUserID(<user_id>).create() is OK(exist return <exist>, new return <new>))
            (DBUserID(<user_id>).create(dict(<the other user_id>)) fobidden!)
        ------
        xxxxxx
        ------
          -[o] should build a proxy API mapping django model API!!!!
    '''

    def __init__(self, user_id=None):
        self.api_be = ("userids", user_id)
        self.api_kw_belong = None


# class DBUserIDSubMixin(object):
#     def setupAPI_kw_belong(self, user_id):
#         self.api_kw_belong = OrderedDict({"userids": user_id})


class DBVisualData(DRFOperate):
    def __init__(self, user_id, date=None):
        self.api_be = ("visualdatas", date)
        self.api_kw_belong = OrderedDict({"userids": user_id})


class DBFans(DRFOperate):
    def __init__(self, user_id, index=None):
        self.api_be = ("fanses", index)
        self.api_kw_belong = OrderedDict({"userids": user_id})


class DBFollow(DRFOperate):
    def __init__(self, user_id, index=None):
        self.api_be = ("follows", index)
        self.api_kw_belong = OrderedDict({"userids": user_id})
