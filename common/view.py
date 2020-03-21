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


class BaseApi():
    name = "base_api"
    description = ""

    class Argument:
        pass

    class Return:
        pass

    def create_class(self, rename, parent_class="Argument,graphene.InputObjectType"):
        class_str = "class {}({}):pass;".format(rename, parent_class)
        exec(class_str)
        return eval(rename)

    @property
    def api(self):
        arg = self.Argument()
        ret = self.Return()
        arg_list = []
        ret_list = []
        for a in arg.__dir__():
            if a[:2] == "__" or a[-2:] == "__":
                continue
            elif "graphene" in str(type(eval("arg.{}".format(a)))) or "graphene" in str(eval("arg.{}".format(a))):
                arg_list.append(a)
        for a in ret.__dir__():

            if a[:2] == "__" or a[-2:] == "__":
                continue

            elif "graphene" in str(type(eval("ret.{}".format(a)))) or "graphene" in str(eval("ret.{}".format(a))):
                ret_list.append(a)
            else:
                print(type(eval("ret.{}".format(a))))
        if ret_list and arg_list:
            return graphene.Field(
                self.create_class(rename="{}_return".format(self.name), parent_class="self.Return,graphene.ObjectType"),
                condition=self.create_class(rename="{}_argument".format(self.name),
                                            parent_class="self.Argument,graphene.InputObjectType")(),
                description=self.description)
        elif ret_list:
            return graphene.Field(
                self.create_class(rename="{}_return".format(self.name), parent_class="self.Return,graphene.ObjectType"),
                description=self.description)
        else:
            raise Exception("该模型{}创建失败: 请给指定返回模型".format(self.name))

    def validate_token(self, info, **kwargs):
        pass

    def validate_privilege(self, token_info, **kwargs):
        pass

    def entrance(self, info, **kwargs):
        self.arguments = kwargs
        self.service_args = self.arguments.get("condition", {}).get("args", {})  ## 定制化
        self.token_info = self.validate_token(info, **kwargs)
        self.prilivege_info = self.validate_privilege(self.token_info, **kwargs)
        return self.deal(self.token_info, self.prilivege_info, **kwargs)

    def deal(self, token_info, prilivege_info, **kwargs):
        return
