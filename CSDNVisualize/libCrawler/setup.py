#!/usr/bin/env python

"""
# file name: setup.py
# Author   : Joseph
# E-mail   : joseph.lin@aliyun.com
#
###
### reference:
###     1. pillow
###     2. https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html
###
"""

import sys

from distutils.core import setup

try:
    setup(name         = 'PersonalData_v0.0.4',
          version      = '0.0.4',
          description  = 'Personal Data on CSDN, first level of Article information',

          author       = 'joseph',
          author_email = 'joseph.lin@aliyun.com',
          url          = 'none',

          # py_modules   = [''],  ## single file.
          packages     = ['personaldata'],
          # package_dir  = {'': 'PersonalData'},
    )
except Exception as err:
    print("setup.py err: ", err)
    sys.exit(1)
