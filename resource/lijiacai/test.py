# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json
import requests

if __name__ == '__main__':
    data = {
        "query": "query query_user{  query_user{    pageInfo{      hasNextPage    }  }}",
        "variables": None,
        "operationName": "query_user"}
    headers = {
        "token": "xxx"
    }
    response = requests.post("http://127.0.0.1:4901/middle_service", json=data, headers=headers)
    print(response)
    print(response.json())
