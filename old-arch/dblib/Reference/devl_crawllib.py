#!/usr/bin/env python3

"""devl_crawllib.py

TODO: N/A
"""
from time import sleep
import sys
import os

# from Crawl.resourcemanage import FakeResourceMange

from sites.jobbole_com.user.index import Subject_Joble_UserInfo
from sites.jobbole_com.article.blog import Subject_Joble_UserArticle
from GUI.web.dbobserver import Observer_Jobbole_UserInfo
from GUI.web.dbobserver import ObserverJobboleArticle

import signal


def sigint_handler(signo, frame):
    ''' show catch Ctrl+C information!'''
    print("\nGoodbay Cruel World.....\n")
    raise SystemExit(1)


def prog_init():
    signal.signal(signal.SIGINT, sigint_handler)


g_options = None

###################################
# Start Code to Monitor by Crawl  #
###################################


#
# run demo:
#
from sites.jobbole_com import schedule as jobbole_schedule


def work():
    ''' -[x] 将 subject 修改为 put 的形式
    subject 的 user id，article 都是已经存在在 db 中的。
    如果有不存在的，应该是执行 “create subject” 这个行为，然后初始化该 subject 示例用来 monitor
    -[o] yeild 的形式，使用 send 激活 update
    （获取一份db 数据副本 -> 刷新页面，获取数据 -> 然后 put/update）
    '''
    # jobbole_article_obs_1 = ObserverJobboleArticle("")
    # jobbole_subj_article_1 = Subject_Joble_UserArticle(
    #     "Chad", "", g_options)
    # jobbole_subj_article_1.register(jobbole_article_obs_1)
    # jobbole_subj_article_1.run()

    jobbole_schedule.setup()
    jobbole_userid_obs = Observer_Jobbole_UserInfo("")
    for jobbole_userid_subject in jobbole_schedule.jobbole_userid_monitor_dict.values():
        jobbole_userid_subject.register(jobbole_userid_obs)
        # jobbole_userid_subject.run()

    from multiprocessing.connection import Listener

    serv = Listener(('', 23881), authkey=b'jobbole')
    while True:
        print("\nListening on 23881...")
        client = serv.accept()
        print("Connection established")
        handle_client(client)


def handle_client(conn):
    try:
        while True:
            recv = conn.recv()
            print("recv: ", recv)

            # {"monitor": "userid", "id": "dimple11"}
            # {"monitor": "articleid", "id": ("dimple11", "<article-id>")}
            if recv.get("monitor", None):
                handler_meth = eval("handler_monitor_" + recv['monitor'])

            # {"new": "userid", "id": "..."}
            # {"new": "articleid", "id": ("user-id", "<article-id>")}
            elif recv.get("new", None):
                handler_meth = eval("handler_new_" + recv['new'])
            else:
                conn.send("Unsupport")
                conn.close()
                break

            ret = handler_meth(recv['id'])
            conn.send(ret)
    except EOFError:
        print("Connection closed")


def handler_monitor_userid(user_id):
    # jobbole_subj_1.run()
    uid_d = jobbole_schedule.jobbole_userid_monitor_dict

    # db_status_code, db_response_data
    return uid_d[user_id].run_update_from_db()


def handler_monitor_articleid(id_tuple):
    user_id, article_id = id_tuple
    return user_id, article_id


def handler_new_userid(user_id):
    jobbole_userid_obs = Observer_Jobbole_UserInfo("")
    _subject, ret = jobbole_schedule.create_new_userid(
        user_id, jobbole_userid_obs)
    return ret  # db server response: status_code, text


if __name__ == '__main__':
    if not __debug__:
        import argparse
        # usage = "Usage: %prog -O -b(--browser) <which browser>"
        # parser = OptionParser(usage=usage)
        parser = argparse.ArgumentParser(description="Specific Browser Type")

        parser.add_argument('-b', "--browser", dest='browser',
                            required=True, action='store',
                            choices={'Chrome', 'Edge', 'Firefox'},
                            # default='Chrome'
                            help="Chrome or Edge(Windows platform) or Firefox")
        args = parser.parse_args()

        g_options = args.browser

    prog_init()

    work()
