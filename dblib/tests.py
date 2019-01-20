#!/usr/bin/env python3

"""dblib/tests.py
Usage:
  .../CSDN-Data/ $ python -m unittest dblib.tests

TODO: n/a
"""

import unittest
import json
import copy


g_userid_data = {
    "user_id": "unittest",
    "name": "Python 功能测试数据用例",
    "visit": 0,
    "rank": 0,
}


def create_unittest_UserID():
    from . import DBUserID
    dbuserid = DBUserID()
    ret = dbuserid.create(g_userid_data)
    status_code, text = ret
    assert int(status_code / 10), 20
    assert True, set(g_userid_data.items()).issubset(set(json.loads(text).items()))

    return json.loads(text)


def remove_unittest_UserID():
    import requests
    url = "http://localhost:8010/api/v1/CSDNCrawler/userids/" + g_userid_data['user_id'] + '/'
    r = requests.delete(url, data=json.dumps({}),
                        headers={'Content-type': 'apllication/json'})
    assert int(r.status_code / 10), 20


@unittest.skip("be test already")
class TestLibDBUserID(unittest.TestCase):
    from . import DBUserID

    # @unittest.skip("be test already, skip create")
    def test_create(self):
        dbuserid = self.DBUserID()
        ret = dbuserid.create(g_userid_data)
        status_code, text = ret
        self.assertEqual(int(status_code / 10), 20, text)

        # DeprecationWarning: assertDictContainsSubset is deprecated
        # self.assertDictContainsSubset(g_userid_data, json.loads(text))
        self.assertTrue(set(g_userid_data.items()).issubset(set(json.loads(text).items())))

    def test_retrieve(self):
        data = {
            "user_id": 'qq_29757283',
            "name": "RDpWTeHM",
        }

        dbuserid = self.DBUserID()
        ret = dbuserid.retrieve(data["user_id"])
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text).items())))

    def test_update(self):
        be_update_data = {
            "user_id": 'be_update_data',
            "name": "unittest 的被更新的数据",
            "rank": 0,
            "visit": 0,
        }
        dbuserid = self.DBUserID()
        ret = dbuserid.create(be_update_data)
        status_code, text = ret
        self.assertEqual(int(status_code / 10), 20, text)

        # do update #######################
        update_data = {
            "user_id": 'be_update_data',
            "visit": 19378,
            "rank": 51810,
        }
        dbuserid = self.DBUserID(update_data["user_id"])
        ret = dbuserid.update(update_data)
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(update_data.items()).issubset(set(json.loads(text).items())))

    '''
    def tearDown(self):
        # remove create
    '''


@unittest.skip("be test already")
class TestLibDBVisualData(unittest.TestCase):
    from . import DBVisualData
    data = {
        "originality": 9,
        "reprint": 23,
        "fans": 3,
        "follow": 1,
        "likes": 0,
        "comments": 2,
        "visitors": 831,
        "rank": 478291,
    }

    def setUp(self):
        self.userid = create_unittest_UserID()

    def tearDown(self):
        remove_unittest_UserID()

    def _create(self):
        dbvisualdata = self.DBVisualData(self.userid["user_id"])
        _data = copy.deepcopy(self.data)
        _data["user_id"] = self.userid['id']
        ret = dbvisualdata.create(_data)
        return ret, _data

    # @unittest.skip("be test already, skip create")
    def test_create(self):
        (status_code, text), _data = self._create()
        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(_data.items()).issubset(set(json.loads(text).items())))

    # @unittest.skip("be test already, skip retrieve")
    def test_retrieve(self):
        (status_code, text), _data = self._create()
        data = json.loads(text)

        # list  #####################
        dbvisualdata = self.DBVisualData(self.userid["user_id"])
        ret = dbvisualdata.retrieve()
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text)[0].items())))

        # detail ####################
        import datetime
        _date = datetime.date.today()
        dbvisualdata = self.DBVisualData(
            self.userid['user_id'], date=_date.strftime("%Y-%m-%d"))
        ret = dbvisualdata.retrieve()
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text).items())))


@unittest.skip("be test already")
class TestLibDBFollow(unittest.TestCase):
    from . import DBFollow
    data = {
        "current_total_follow_num": 2,
        "user_id": "follow1",
        "name": "关注 1 号",
    }

    def setUp(self):
        self.userid = create_unittest_UserID()

    def tearDown(self):
        remove_unittest_UserID()

    def _create(self):
        dbfollow = self.DBFollow(self.userid["user_id"])
        _data = copy.deepcopy(self.data)
        _data["followed_by"] = self.userid['id']
        ret = dbfollow.create(_data)
        return ret, _data

    # @unittest.skip("be test already, skip create")
    def test_create(self):
        (status_code, text), _data = self._create()
        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(_data.items()).issubset(set(json.loads(text).items())))

    def test_retrieve(self):
        (status_code, text), _data = self._create()
        data = json.loads(text)

        # list  #####################
        dbfollow = self.DBFollow(self.userid["user_id"])
        ret = dbfollow.retrieve()
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text)[0].items())))

        # detail ####################
        dbfollow = self.DBFollow(self.userid['user_id'], index=1)
        ret = dbfollow.retrieve()
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text).items())))


# @unittest.skip("be test already")
class TestLibDBFans(unittest.TestCase):
    from . import DBFans
    data = {
        "current_total_fans_num": 2,
        "user_id": "fans1",
        "name": "关注 1 号",
    }

    def setUp(self):
        self.userid = create_unittest_UserID()

    def tearDown(self):
        remove_unittest_UserID()

    def _create(self):
        dbfans = self.DBFans(self.userid["user_id"])
        _data = copy.deepcopy(self.data)
        _data["fans_of"] = self.userid['id']
        ret = dbfans.create(_data)
        return ret, _data

    # @unittest.skip("be test already, skip create")
    def test_create(self):
        (status_code, text), _data = self._create()
        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(_data.items()).issubset(set(json.loads(text).items())))

    def test_retrieve(self):
        (status_code, text), _data = self._create()
        data = json.loads(text)

        # list  #####################
        dbfans = self.DBFans(self.userid["user_id"])
        ret = dbfans.retrieve()
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text)[0].items())))

        # detail ####################
        dbfans = self.DBFans(self.userid['user_id'], index=1)
        ret = dbfans.retrieve()
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(data.items()).issubset(set(json.loads(text).items())))


if __name__ == '__main__':
    unittest.main()
