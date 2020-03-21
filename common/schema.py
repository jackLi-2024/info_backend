#!/usr/bin/env python
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
import logging

users = os.listdir("resource")
result = []
for user in users:
    if "py" in user or "pyc" in user:
        continue
    try:
        vs = os.listdir("resource/{}/view".format(user))
    except Exception as e:
        # logging.exception(e)
        vs = []
    for v in vs:
        if ".py" in v:
            v = v.replace(".py", "").replace(".pyc", "")
        else:
            continue
        try:
            exec("from resource.{}.view.{} import *".format(user, v))
        except Exception as e:
            print(str(e))
            # logging.exception(e)
            continue

vars = dict(locals())
for k, v in vars.items():
    try:
        # print(str(v.__bases__))
        # if v.__base__.__name__ == "BaseApi":
        if "BaseApi" in str(v.__bases__):
            result.append(v)
    except Exception as e:
        # logging.exception(e)
        pass
res = {}
for Api in result:
    name = Api().name
    exec("{}_m = Api()".format(name))
    res[name] = name + "_m"


class QueryMutation(graphene.ObjectType):
    for k, v in res.items():
        try:
            exec("{} = {}.api".format(k, v))
            exec("def resolve_{}(self, info, **kwargs): return {}.entrance(info, **kwargs)".format(k, v))
        except Exception as e:
            logging.exception(e)
            pass


schema = graphene.Schema(query=QueryMutation, mutation=QueryMutation, auto_camelcase=False)
