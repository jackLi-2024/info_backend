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
import graphene
from common.view import BaseApi


class A():
    def run(self):
        pass


class CApi(BaseApi, A):
    name = "c_api"
    description = "测试3"

    class Argument:
        pass

    class Return:
        age = graphene.String()

    def deal(self, token, **kwargs):
        print(**kwargs)
        return {"b": 1}
