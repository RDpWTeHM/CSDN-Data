#!/usr/bin/env python3
""" PersonalData Tests Case

 for build a robustness crawler CSDN system.
 test case duplicate bug and report is pass or not.
"""

import os
import sys
import unittest

from PersonalData.webpage import PersonCSDN
from PersonalData.webpage import UserData
from PersonalData.webpage import SocialData
from PersonalData.blogpage import PersonalArticles
from PersonalData.utils import *

from PersonalData.exceptions import *


class PersonCSDNTest(unittest.TestCase):
    """ test PersonCSDN class """

    @unittest.skip("skipped test")
    def test_can_get_UserData(self):
        homepage_data = PersonCSDN(USER_ID)
        homepage_data.syncUserData()

        # last version to recive data for compare
        # ...

        # Compare equal?

        return True

    @unittest.skipUnless(sys.platform == 'linux', 'linux can use this test')
    def test_can_handle_timeout_by_IPC(self):
        if __debug__:
            print("[Info] running test PersonCSDN can handler timeout by IPC", file=sys.stderr)

        # -[/] shutdown the network -> make timeout
        os.system("sudo ifconfig ens33 down")  # vmware 虚拟机上默认名为 ens33

        USER_ID = 'qq_29757283'

        homepage_data = PersonCSDN(USER_ID)
        ''' .syncUserData() 做了获取 page source 和 解析出数据的动作。
         如果 获取 page source 的时候，IPC 给的是一个 timeout，
         该 function 应当正确处理 - 抛出 timeout 异常
        '''
        try:
            homepage_data.syncUserData()
        except CrawlerTimeoutError as e:
            self.assertEqual(str(e), "timeout")
        else:
            self.assertFalse("Did you shutdown the Network yet???"
                             "this TestCase need make timeout happen!")


class ConcurrentTest(unittest.TestCase):
    """ 测试并发处理大多是以概率性出现的问题
    虽然是概率性出现的，但是程序应当不要让问题（概率性）出现，
    以及要正确处理当这类问题真的在考虑之外出现的时候。
    """

    def test_server_refuse_IPC_connection(self):
        ''' server 在多线程内建立 IPC（multiprocessing.connection）链接，
        目前推测是线程不安全的问题导致链接建立失败 - client 当作 server refuse connection。
        '''
        '''
        import socket
        from multiprocessing.connection import Client
        from multiprocessing import Process

        ## 使用 socket 协商多个 IPC。


        ## 多个“进程”（同时）和 server 建立 IPC 链接，发布请求网页 page source 任务
        '''
        from multiprocessing import Process
        for _ in range(4):  # loop 4 times ensure can dupcate the issue
            missions = ['qq_29757283', 'jinjianghai', 'lizhe1985', 'valada',
                        'shanliangliuxing', 'mp624183768', 'u012515223',
                        'ztf312',
                        ]

            def handler_mission(user_id):
                myCSDNInfo = UserData(user_id, doDebug=True, )
                dict_ = myCSDNInfo.quikSyncCSDNData()
                print(dict_)

            processes = []
            for mission in missions:
                new_Process = Process(target=handler_mission,
                                      args=(mission, ), )
                processes.append(new_Process)

            for _process in processes:
                _process.start()

            for _process in processes:
                _process.join()


if __name__ == '__main__':
    unittest.main()
