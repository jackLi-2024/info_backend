# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""
import datetime
import os
import re
import sys
import json
import graphene
from common.view import BaseApi
from resource.lijiacai.utils import utils
from sql import *
from sql.aggregate import *
from sql.functions import *
from sql.conditionals import *


class RegisteUser(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "RegisteUser"
    description = "注册用户(done)"

    table = Table("users")

    class Argument:
        # uid = graphene.String(description="用户id（基于手机号的加密）")
        nick = graphene.String(description="用户昵称")
        avatar = graphene.String(description="头像(上传baseb4)")
        create_time = graphene.String(description="创建时间")
        phone = graphene.String(description="用户手机号", required=True)
        password = graphene.String(description="用户登录密码", required=True)
        status = graphene.Int(description="用户状态(1:可以使用 0：不可使用)", default=1)

    class Return:
        succ = graphene.Boolean(description="操作状态True表示成功")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        args = self.arguments
        data = {}
        for k, v in args.items():
            data[eval(f"self.table.{k}")] = v
        data[self.table.uid] = self.get_md5(args.get("phone"))
        columns, values = self.split_columns_values(data=data)
        sql = self.deal_sql(self.table.insert(columns=columns, values=[values]))
        self.execute(sql)
        return {"succ": True}


class LoginUser(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "LoginUser"
    description = "登录用户(done)"

    table = Table("users")

    eq_argument = {
        "phone": table.phone,
        "password": table.password,
    }

    class Argument:
        # uid = graphene.String(description="用户id（基于手机号的加密）")
        # nick = graphene.String(description="用户昵称")
        # avatar = graphene.String(description="头像(上传baseb4)")
        # create_time = graphene.String(description="创建时间")
        phone = graphene.String(description="用户手机号", required=True)
        password = graphene.String(description="用户登录密码", required=True)
        # status = graphene.Int(description="用户状态(1:可以使用 0：不可使用)", default=1)

    class Return:
        uid = graphene.String(description="用户id（基于手机号的加密）")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        sql = self.deal_sql(self.data_group.select(where=self.where))
        self.execute(sql)
        rows = self.read_all()
        return {"uid": rows[0].get("uid")}


class ModifyUser(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "ModifyUser"
    description = "修改用户(done)"

    table = Table("users")
    eq_argument = {
        "uid": table.uid
    }

    class Argument:
        uid = graphene.String(description="用户id（基于手机号的加密）", required=True)
        nick = graphene.String(description="用户昵称")
        avatar = graphene.String(description="头像(上传baseb4)")
        create_time = graphene.String(description="创建时间")
        phone = graphene.String(description="用户手机号", required=True)
        password = graphene.String(description="用户登录密码", required=True)
        status = graphene.Int(description="用户状态(1:可以使用 0：不可使用)", default=1)

    class Return:
        succ = graphene.Boolean(description="操作状态True表示成功")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        data = {}
        for k, v in self.arguments.items():
            if k == "eid":
                continue
            data[eval(f"self.table.{k}")] = v
        columns, values = self.split_columns_values(data=data)
        sql = self.deal_sql(self.table.update(columns=columns, values=values, where=self.where))
        self.execute(sql)
        return {"succ": True}


class SearchUserByUser(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "SearchUserByUser"
    description = "用户查询用户信息(done)"

    table = Table("users")
    eq_argument = {
        "uid": table.uid,
        # "nick": table.nick,
        # "avatar": table.avatar,
        # "phone": table.phone,
        # "password": table.password,
        # "status": table.status
    }

    class Argument:
        uid = graphene.String(description="用户id（基于手机号的加密）")
        # nick = graphene.String(description="用户昵称")
        # avatar = graphene.String(description="头像(上传baseb4)")
        # create_time = graphene.String(description="创建时间")
        # phone = graphene.String(description="用户手机号")
        # password = graphene.String(description="用户登录密码")
        # status = graphene.Int(description="用户状态(1:可以使用 0：不可使用)")

    class Return:
        # class SearchUserReturn(graphene.ObjectType):
        #     nick = graphene.String(description="用户昵称")
        #     avatar = graphene.String(description="头像(上传baseb4)")
        #     create_time = graphene.String(description="创建时间")
        #     phone = graphene.String(description="用户手机号")
        #     password = graphene.String(description="用户登录密码")
        #     status = graphene.Int(description="用户状态(1:可以使用 0：不可使用)")
        #
        # rows = graphene.List(SearchUserReturn, description="查询列表")
        nick = graphene.String(description="用户昵称")
        avatar = graphene.String(description="头像(上传baseb4)")
        create_time = graphene.String(description="创建时间")
        phone = graphene.String(description="用户手机号")
        password = graphene.String(description="用户登录密码")
        status = graphene.Int(description="用户状态(1:可以使用 0：不可使用)")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        self.reset_page_size()
        sql = self.deal_sql(
            self.data_group.select(where=self.where, order_by=self.order, limit=self.limit, offset=self.offset))
        self.execute(sql)
        rows = self.read_all()
        return rows[0]


class PublishInfo(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "PublishInfo"
    description = "信息发布(done)"

    table = Table("info")

    class Argument:
        uid = graphene.String(description="用户id（基于手机号的加密）", required=True)
        title = graphene.String(description="标题", required=True)
        name = graphene.String(description="姓名", required=True)
        phone = graphene.String(description="手机号", required=True)
        # create_time = graphene.String(description="创建时间")
        # update_time = graphene.String(description="修改时间")
        address = graphene.String(description="地址", required=True)
        # status = graphene.Int(description="信息状态(1:待确认 2：已确认 3：取消)")

    class Return:
        succ = graphene.Boolean(description="操作状态True表示成功")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        args = self.arguments
        data = {}
        for k, v in args.items():
            if k == "uid":
                continue
            data[eval(f"self.table.{k}")] = v
        columns, values = self.split_columns_values(data=data)
        sql = self.deal_sql(self.table.insert(columns=columns, values=[values]))
        self.execute(sql)
        return {"succ": True}


class ModifyInfoByUser(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "ModifyInfoByUser"
    description = "用户修改信息(done)"

    table = Table("info")

    eq_argument = {
        "id": table.id
    }

    class Argument:
        id = graphene.Int(description="自增id", required=True)
        uid = graphene.String(description="用户id（基于手机号的加密）", required=True)
        title = graphene.String(description="标题", required=True)
        name = graphene.String(description="姓名", required=True)
        phone = graphene.String(description="手机号", required=True)
        # create_time = graphene.String(description="创建时间")
        # update_time = graphene.String(description="修改时间")
        address = graphene.String(description="地址", required=True)
        # status = graphene.Int(description="信息状态(1:待确认 2：已确认 3：取消)")

    class Return:
        succ = graphene.Boolean(description="操作状态True表示成功")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        args = self.arguments
        data = {}
        for k, v in args.items():
            if k == "uid":
                continue
            data[eval(f"self.table.{k}")] = v
        data[self.table.update_time] = str(datetime.datetime.now())
        columns, values = self.split_columns_values(data=data)
        sql = self.deal_sql(self.table.insert(columns=columns, values=[values]))
        self.execute(sql)
        return {"succ": True}


class SearchInfoByUser(utils.BusinessInfo, BaseApi, utils.MySQLCrud):
    name = "SearchInfoByUser"
    description = "用户查询发布信息(done)"

    table = Table("info")
    eq_argument = {
        "uid": table.uid,
        "title": table.title,
        "name": table.name,
        "phone": table.phone,
        "create_time": table.create_time,
        "update_time": table.update_time,
        "address": table.address,
        "status": table.status
    }

    class Argument:
        id = graphene.Int(description="自增id")
        uid = graphene.String(description="用户id（基于手机号的加密）", required=True)
        title = graphene.String(description="标题")
        name = graphene.String(description="姓名")
        phone = graphene.String(description="手机号")
        create_time = graphene.String(description="创建时间")
        update_time = graphene.String(description="修改时间")
        address = graphene.String(description="地址")
        status = graphene.Int(description="信息状态(1:待确认 2：已确认 3：取消)")

        page_size = graphene.Int(description="一页总数",default=10)
        page_num = graphene.Int(description="第几页",default=1)

    class Return:
        class SearchInfoByUserReturn(graphene.ObjectType):
            id = graphene.Int(description="自增id")
            uid = graphene.String(description="用户id（基于手机号的加密）")
            title = graphene.String(description="标题")
            name = graphene.String(description="姓名")
            phone = graphene.String(description="手机号")
            create_time = graphene.String(description="创建时间")
            update_time = graphene.String(description="修改时间")
            address = graphene.String(description="地址")
            status = graphene.Int(description="信息状态(1:待确认 2：已确认 3：取消)")

        rows = graphene.List(SearchInfoByUserReturn, description="查询列表")

    def validate_privilege(self, token_info, **kwargs):
        pass

    def deal(self, token_info, prilivege_info, **kwargs):
        self.validate_graphql_api(name=self.name)
        return self.run()

    def dealer(self):
        # self.reset_page_size()
        sql = self.deal_sql(
            self.data_group.select(where=self.where, order_by=self.order, limit=self.limit, offset=self.offset))
        self.execute(sql)
        rows = self.read_all()
        return {"rows": rows}
