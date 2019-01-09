#!/usr/bin/env python3

"""
 this is configuration file by python
"""

import sys

from collections import namedtuple


Configuration = namedtuple('Configuration',
                           ['SHELVE_DB_PATH',
                            'ALL_USER_FILE',
                            'DJANGO_SERVER',
                            'DJANGO_ARTICLES_URL',
                            'THREAD_NUM',
                            'LOGGING_FILE',
                            'NOSERVER_BASEWAITE',
                            ])

conf = Configuration(
    SHELVE_DB_PATH="./tmp",
    ALL_USER_FILE='UserID',

    DJANGO_SERVER="http://localhost:8010",
    DJANGO_ARTICLES_URL="CSDNCrawler/loopArticles",

    THREAD_NUM=2,

    LOGGING_FILE="/mnt/banq_16g/CSDN-Data/log/client_active_daemon/20190107_1917.log",

    NOSERVER_BASEWAITE=30,  # no django server running, wait increase by 30s
)

#
# check enviornment!
#


if __name__ == "__main__":
    print("Not usage like this!")
    sys.exit(1)
