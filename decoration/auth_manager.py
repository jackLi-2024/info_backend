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
import requests


class Request():

    def POST_json(self, url, **kwargs):
        try:
            return requests.post(url=url, **kwargs).json()
        except Exception as e:
            raise Exception("请求失败")


class Graphql(Request):
    def general(self, name, return_model, url, condition=None, include_args=True):
        params = self.get_params(name=name, return_model=return_model, include_args=include_args, condition=condition)
        return self.POST_json(url=url, json=params)

    def create_gql(self, name, return_model, include_args=True):
        if include_args:
            args_str = f"($condition:{name}_argument)"
            condition_str = "(condition:$condition)"
        else:
            args_str = ""
            condition_str = ""
        return f"query {name}{args_str}" + \
               "{ " + \
               f"{name}{condition_str}" + " { " + f"{return_model}" + " } " + \
               " }"

    def get_params(self, name, return_model, include_args=True, condition=None):
        params = {
            "query": self.create_gql(name=name, return_model=return_model, include_args=include_args),
            "variables": condition,
            "operationName": name
        }
        return params


class AuthToken(Graphql):
    token_url = "http://cq-platform.pand-iot.com/auth2/graphql_doc_ui"

    def GenerateToken(self, condition=None, include_args=True):
        name = "GenerateToken"
        return_model = "access_token fresh_token"
        return self.general(name=name, return_model=return_model, url=self.token_url, condition=condition,
                            include_args=include_args)

    def FreshToken(self, condition=None, include_args=True):
        name = "FreshToken"
        return_model = "access_token fresh_token"
        return self.general(name=name, return_model=return_model, url=self.token_url, condition=condition,
                            include_args=include_args)

    def ValidateToken(self, condition=None, include_args=True):
        name = "ValidateToken"
        return_model = "dec_data user_id"
        return self.general(name=name, return_model=return_model, url=self.token_url, condition=condition,
                            include_args=include_args)

    def LogoutToken(self, condition=None, include_args=True):
        name = "LogoutToken"
        return_model = "action"
        return self.general(name=name, return_model=return_model, url=self.token_url, condition=condition,
                            include_args=include_args)


class AuthManager(Graphql):
    auth_url = "http://cq-platform.pand-iot.com/auth2/graphql_doc_ui"

    def AddMenu(self, condition=None, include_args=True):
        name = "AddMenu"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def DeleteMenu(self, condition=None, include_args=True):
        name = "DeleteMenu"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def UpdateMenu(self, condition=None, include_args=True):
        name = "UpdateMenu"
        return_model = "log_id log_type log_name identify status plat parent_log_id log_detail"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchMenu(self, condition=None, include_args=True):
        name = "SearchMenu"
        return_model = "rows{ log_id log_type log_name identify status plat parent_log_id log_detail}"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def AddUserGroupData(self, condition=None, include_args=True):
        name = "AddUserGroupData"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def DeleteUserGroupData(self, condition=None, include_args=True):
        name = "DeleteUserGroupData"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def UpdateUserGroupData(self, condition=None, include_args=True):
        name = "UpdateUserGroupData"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchUserGroupData(self, condition=None, include_args=True):
        name = "SearchUserGroupData"
        return_model = "rows{  user_group_id user_group_type user_group_name plat user_group_data user_group_detail }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchUserGroup(self, condition=None, include_args=True):
        name = "SearchUserGroup"
        return_model = "rows{  user_group_type user_group_name plat }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def AddDataGroupData(self, condition=None, include_args=True):
        name = "AddDataGroupData"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def DeleteDataGroupData(self, condition=None, include_args=True):
        name = "DeleteDataGroupData"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def UpdateDataGroupData(self, condition=None, include_args=True):
        name = "UpdateDataGroupData"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchDataGroupData(self, condition=None, include_args=True):
        name = "SearchDataGroupData"
        return_model = "rows { data_group_id data_group_type data_group_name data_group_data plat data_group_detail }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def AddResourcePrivilege(self, condition=None, include_args=True):
        name = "AddResourcePrivilege"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def DeleteResourcePrivilege(self, condition=None, include_args=True):
        name = "DeleteResourcePrivilege"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def AddDataPrivilege(self, condition=None, include_args=True):
        name = "AddDataPrivilege"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def DeleteDataPrivilege(self, condition=None, include_args=True):
        name = "DeleteDataPrivilege"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def AddUserPrivilege(self, condition=None, include_args=True):
        name = "AddUserPrivilege"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def DeleteUserPrivilege(self, condition=None, include_args=True):
        name = "DeleteUserPrivilege"
        return_model = "succ"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchUserResourcePrivilege(self, condition=None, include_args=True):
        name = "SearchUserResourcePrivilege"
        return_model = "rows{ user_id user_no plat user_group_id user_detail resource_privilege_id resource_privilege_detail log_id log_name log_type parent_log_id identify status }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchUserDataPrivilege(self, condition=None, include_args=True):
        name = "SearchUserDataPrivilege"
        return_model = "rows{  user_id user_no plat user_group_id user_detail resource_privilege_id resource_privilege_detail data_privilege_id data_privilege_detail data_group_id data_group_data data_group_detail data_group_name data_group_type log_id log_name log_type parent_log_id identify status }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchUserGroupResourcePrivilege(self, condition=None, include_args=True):
        name = "SearchUserGroupResourcePrivilege"
        return_model = "rows{  user_group_id user_group_type user_group_name plat user_group_data user_group_detail resource_privilege_id resource_privilege_detail log_id log_name log_type parent_log_id identify status }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def SearchUserGroupDataPrivilege(self, condition=None, include_args=True):
        name = "SearchUserGroupDataPrivilege"
        return_model = "rows{ user_group_id user_group_type user_group_name plat user_group_data user_group_detail resource_privilege_id resource_privilege_detail data_privilege_id data_privilege_detail data_group_id data_group_data data_group_detail data_group_name data_group_type log_id log_name log_type parent_log_id identify status }"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def CheckUserDataPrivilege(self, condition=None, include_args=True):
        name = "CheckUserDataPrivilege"
        return_model = "exist"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)

    def CheckUserResourcePrivilege(self, condition=None, include_args=True):
        name = "CheckUserResourcePrivilege"
        return_model = "exist"
        return self.general(name=name, return_model=return_model, url=self.auth_url, condition=condition,
                            include_args=include_args)


class Auth(AuthToken, AuthManager):
    pass


def test1():
    condition = {
        "condition": {
            "enc_data": "lijiacai",
            "user_id": "1",
            "app_id": "test"
        }
    }
    auth = Auth()
    result = auth.GenerateToken(condition=condition)
    print(result)
    to = result["data"]["GenerateToken"]["access_token"]
    condition = {
        "condition": {"token": to}
    }
    result = auth.ValidateToken(condition=condition)
    print(result)


def test2():
    result = AuthManager().SearchDataGroupData(include_args=False)
    print(result)


if __name__ == '__main__':
    test1()
    # test2()
