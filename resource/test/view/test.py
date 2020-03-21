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


class BApi(BaseApi):
    name = "b_api"
    description = "测试2"

    class Argument:
        pass

    class Return:
        d = graphene.Int()

    def deal(self, token, **kwargs):
        print(**kwargs)
        return {"b": 1}
