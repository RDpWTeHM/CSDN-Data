#!/usr/bin/env python3

"""dblib/tests.py
Usage:
  .../CSDN-Data/ $ python -m unittest dblib.tests

TODO: n/a
"""

import unittest
import json

g_userid_data = {
    "user_id": "testcase",
    "name": "Python 功能测试数据用例",
    "visit": 0,
    "rank": 0,
}


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
        ret = dbuserid.update(update_data)
        status_code, text = ret

        self.assertEqual(int(status_code / 10), 20, text)
        self.assertTrue(set(update_data.items()).issubset(set(json.loads(text).items())))

    '''
    def tearDown(self):
        # remove create
    '''


# class TestLibDBVisualData(unittest.TestCase):
# class TestLibDBFollow(unittest.TestCase):
# class TestLibDBFans(unittest.TestCase):


if __name__ == '__main__':
    unittest.main()
