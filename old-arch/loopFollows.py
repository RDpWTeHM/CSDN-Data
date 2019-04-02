#!/usr/bin/env python3

"""
"""
import sys
import os


def main():
    import requests
    def gen_url(pk):
        return "http://localhost:8010/CSDNCrawler/userid/" + \
               str(pk) + "/crawl/follows/"

    _pk=7110
    r = requests.get(gen_url(_pk))
    continuous_fail = 0
    while continuous_fail < 3:
        continuous_fail = continuous_fail + 1 if r.status_code != 200 else 0
        _pk += 1
        print(_pk, "; ", end="", flush=True)
        r = requests.get(gen_url(_pk))
        


if __name__ == "__main__":
    main()
    """
    import time
    _i = 0
    while _i<10:
        print(_i, "; ", end="", flush=True)
        _i += 1
        time.sleep(0.5)
    """

