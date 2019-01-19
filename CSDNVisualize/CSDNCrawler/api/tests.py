from django.test import TestCase

# Create your tests here.
"""CSDNVisualize/CSDNCrawler/api/tests.py

TODO:
    n/a
"""
import unittest
import os
import sys
from django.utils import timezone
import copy
import json

#
# model packages
#
# from ..models import Site
from ..models import UserID

from ..models import Fans
# from ..models import Follow


#
# utils for unittest
#
g_userid_data = {
    "user_id": "RDpWTeHM",
    "name": "Joseph Lin",
}

IS_API_CHAR_INDEX = True


def create_db_model_UserID(userid_data=None, foreignkey=None):
    global g_userid_data
    data = {}
    if userid_data:
        data = copy.deepcopy(userid_data)
    else:
        data = copy.deepcopy(g_userid_data)

    if foreignkey:
        data.update(copy.deepcopy(foreignkey))

    return UserID.objects.create(**data)


class FansAPITest(TestCase):
    fans_1 = {
        "user_id": "fans_id_1",
        "name": "我是粉丝1号",
    }

    fans_2 = {
        "user_id": "fans_id_2",
        "name": "i am fans number 2",
    }

    def create_DB_model_Fans(self, fans, follow_to_userid):
        fans["fans_of"] = follow_to_userid
        return Fans.objects.create(**fans)

    def _setup(self):
        '''FansAPITest >_setup method
        Returns:
            tuple -- <UserID object>
        '''
        return create_db_model_UserID()

    def _gen_fans_api_url(self, userid, fans_idx=None, foreignkey=None):
        _common_url_head = "/api/v1/CSDNCrawler/userids/"
        if not fans_idx and IS_API_CHAR_INDEX:
            return _common_url_head +\
                   "{}/fanses/".format(userid.user_id)

        if fans_idx and IS_API_CHAR_INDEX:
            return _common_url_head +\
                   "{}/fanses/{}/".format(userid.user_id, fans_idx)
        return False

    def test_create(self):
        userid_obj = self._setup()
        data = copy.deepcopy(self.fans_1)
        data["fans_of"] = userid_obj.id  # now id(pk); update as string later
        resp = self.client.post(self._gen_fans_api_url(userid_obj), data)
        self.assertEqual(
            int(resp.status_code / 10), 20,
            "server response {}@{}".format(resp.status_code, resp.content))

        # under 3.6 need resp.content.decode('utf-8')!!
        self.assertDictContainsSubset(data, json.loads(resp.content.decode('utf-8')))

    # @unittest.skip("not achive yet")
    def test_read(self):
        # prepare data ###################
        userid_obj = self._setup()
        fans_obj = self.create_DB_model_Fans(self.fans_1, userid_obj)
        fans_data = copy.deepcopy(self.fans_1)
        fans_data["fans_of"] = fans_obj.fans_of.id

        # list api #####
        resp = self.client.get(self._gen_fans_api_url(userid_obj))
        # assert
        self.assertEqual(
            int(resp.status_code / 10), 20,
            "server response {}@{}".format(resp.status_code, resp.content))
        self.assertDictContainsSubset(fans_data, json.loads(resp.content.decode('utf-8'))[0])

        # detail api ####
        # "/api/v1/CSDNCrawler/userids/<user id>/fans/<index>/"
        resp = self.client.get(self._gen_fans_api_url(userid_obj, fans_idx=1))
        # assert
        self.assertEqual(
            int(resp.status_code / 10), 20,
            "server response {}@{}".format(resp.status_code, resp.content))
        self.assertDictContainsSubset(fans_data, json.loads(resp.content.decode('utf-8')))

    def test_update(self):
        src_data = self.fans_1
        dst_data = self.fans_2

        # prepare data ###################
        userid_obj = self._setup()
        fans_obj = self.create_DB_model_Fans(src_data, userid_obj)

        dst_data = copy.deepcopy(dst_data)
        dst_data["fans_of"] = fans_obj.fans_of.id

        #
        # do update
        #
        content_type = 'application/json'
        resp = self.client.put(
            self._gen_fans_api_url(userid_obj, fans_idx=1),
            json.dumps(dst_data), content_type=content_type)

        # check pass or not #################
        self.assertEqual(
            resp.status_code, 200,
            "server response {}@{}".format(resp.status_code, resp.content))
        self.assertDictContainsSubset(dst_data, json.loads(resp.content.decode('utf-8')))
