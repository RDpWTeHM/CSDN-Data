"""super-spider/observers/proxy.py

n/a
"""

import os
import sys

import requests
import json


rest_auth_username = "admin"
rest_auth_password = "Viusai//"
json_header = {'Content-Type': 'application/json'}
domain = "http://localhost:8010"


def get_rest_auth_key_dict(username, password):
    '''n/a '''
    url = "/api/rest_auth/login/"
    r = requests.post(domain + url, headers=json_header,
                      data=json.dumps({"username": rest_auth_username,
                                       "password": rest_auth_password, }))

    def parser_response_key_in_d(r):
        return json.loads(r.text)['key']

    return {'Authorization': 'Token ' + parser_response_key_in_d(r)}


def get_rest_framework_user_id_index(user_id):
    url = "/api/v1/CSDNCrawler/userids/{}/".format(user_id)
    full_path = domain + url
    r = requests.get(full_path,
                     headers=get_rest_auth_key_dict(rest_auth_username,
                                                    rest_auth_password), )
    data = json.loads(r.text)
    print("{} > data: {}".format("get_rest_framework_user_id_index", data))
    ret = data['id']
    return ret


def crawl_visualdata_to_jsondict(data, user_id):
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
        dstdata['user_id'] = get_rest_framework_user_id_index(user_id)
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
    header = json_header
    header.update(
        get_rest_auth_key_dict(rest_auth_username, rest_auth_password))

    url = "/api/v1/CSDNCrawler/userids/{}/visualdatas/".format(user_id)
    full_path = domain + url
    r = requests.post(full_path, data=json.dumps(data), headers=header)

    return (r.status_code, r.text)
