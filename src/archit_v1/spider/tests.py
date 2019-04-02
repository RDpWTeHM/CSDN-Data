# spider/tests.py
"""
Usage:
  spider/$ python -m unittest tests.py
"""

import unittest

import requests

from website.csdn.userhome import UserInfoium
import spider


class TestCrawlUserInfo(unittest.TestCase):
    def setUp(self):
        self.browser = spider._create_new_browser()

    def test_crawl_csdn_user_home_page_info(self):
        user_id = "qq_29757283"
        # development crawl lib result
        result = spider.get_crawl_csdn_userinfo(user_id, self.browser)

        # test result
        r = requests.get(UserInfoium(user_id, self.browser)._gen_url(),
                         timeout=5)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        test_result = r.text

        # test
        for k, v in result.items():
            self.assertIn(str(v), test_result)

    def tearDown(self):
        self.browser.quit()


if __name__ == '__main__':
    unittest.main()
