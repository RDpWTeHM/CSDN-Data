#!/usr/bin/env python3

"""
 this is configuration file by python
"""

import sys

from collections import namedtuple


Configuration = namedtuple('Configuration',
                           ['MAX_BROWSER_RUN',
                            'PIDFILE',
                            'LOG_PATH',
                            'STD_FILE',
                            'NEGOTIATE_DOMAIN', 'NEGOTIATE_PORT',
                            'STATUS_DOMAIN', 'STATUS_PORT',
                            ])

conf = Configuration(
    MAX_BROWSER_RUN=2,
    PIDFILE="/tmp/daemon.pid",
    # DEBUG_BROWSER=,
    LOG_PATH="/mnt/banq_16g/CSDN-Data/log/daemonize_use_threadpool/",
    STD_FILE="20190107_1917.log",
    NEGOTIATE_DOMAIN='', NEGOTIATE_PORT=50007,
    STATUS_DOMAIN='', STATUS_PORT=50008,
)

#
# check enviornment!
#


if __name__ == "__main__":
    print("Not usage like this!")
    sys.exit(1)
