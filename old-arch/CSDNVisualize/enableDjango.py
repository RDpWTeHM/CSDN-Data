#!/usr/bin/env python3

"""
"""

import sys
import os

try:
	redirectIO = "> {} 2>&1 &".format(sys.argv[1])
	cmd = "python3 manage.py runserver 0.0.0.0:8010 {}".format(redirectIO)

	os.system(cmd)
	print("run: '{}'".format(cmd))
except IndexError:
	print("usage: %s <django log file-path>" % sys.argv[0], file=sys.stderr)
	sys.exit(1)

