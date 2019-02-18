"""super-spider/observers/proxy.py

n/a
"""

import os
import sys

import requests
import json


def get_rest_auth_key(username, password):
    '''n/a '''
    # r = requests.post()
    r = None

    def parser_rquest_result_get_rest_auth_key(r):
        return "ff1316bf7b3e2502b9ac85cbddcee65db17f007b"

    return parser_rquest_result_get_rest_auth_key(r)


def crawl_visualdata_to_jsondict(data):
    '''data = {
        "originality": 94,
        "reprint": 14,
        "fans": 11,
        "follow": 20,
        "likes": 48,
        "comments": 9,
        "csdnlevel": 4,
        "visitors": 22613,
        "rank": 50774,
        "user_id": 1
    }
    '''
    dstdata = {}
    try:
        dstdata['originality'] = int(data['originality'])
        dstdata['reprint'] = int(data['reprint'])
        dstdata['fans'] = int(data['fans'])
        dstdata['follow'] = int(data['follow'])
        dstdata['likes'] = int(data['likes'])
        dstdata['comments'] = int(data['comments'])
        dstdata['visitors'] = int(data['visitors'])
        dstdata['rank'] = int(data['rank'])
        dstdata['user_id'] = 1
    except Exception as err:
        import traceback; traceback.print_exc();
        raise
    return dstdata


'''format of token key for POST

Authorization: Token ff1316bf7b3e2502b9ac85cbddcee65db17f007b
'''


def send_visualdata2server(data, user_id):
    '''
    usage:
        send_visualdata2server(crawl_visualdata_to_jsondict(src_data))
    '''
    header = {"Authorization": "Token ",
              'Content-Type': 'application/json', }
    header["Authorization"] += get_rest_auth_key("admin", "Viusai//")

    url = "http://localhost:8010/api/v1/CSDNCrawler/userids/{}/visualdatas/".format(user_id)
    r = requests.post(url, data=json.dumps(data), headers=header)

    return (r.status_code, r.text)
