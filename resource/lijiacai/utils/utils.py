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
import random
import re
import sys
import json
import time
import requests
import pymysql
import logging
import configparser
import jwt
import hashlib
import redis
import shortuuid
from hashids import Hashids
from sql import *
from sql.aggregate import *
from sql.conditionals import *
from sql.operators import *
import graphene


def get_config(conf_file="./configure/main.conf"):
    config = configparser.ConfigParser()
    config.read(conf_file)
    info = config._sections
    return info


config = get_config()


class RedisDB():
    def __init__(self, host='localhost', port=6379,
                 db=0, password=None, socket_timeout=None,
                 socket_connect_timeout=None,
                 socket_keepalive=None, socket_keepalive_options=None,
                 connection_pool=None, unix_socket_path=None,
                 encoding='utf-8', encoding_errors='strict',
                 charset=None, errors=None,
                 decode_responses=False, retry_on_timeout=False,
                 ssl=False, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs='required', ssl_ca_certs=None,
                 max_connections=None):
        self.client = redis.Redis(host=host, port=port,
                                  db=db, password=password, socket_timeout=socket_timeout,
                                  socket_connect_timeout=socket_connect_timeout,
                                  socket_keepalive=socket_keepalive, socket_keepalive_options=socket_keepalive_options,
                                  connection_pool=connection_pool, unix_socket_path=unix_socket_path,
                                  encoding=encoding, encoding_errors=encoding_errors,
                                  charset=charset, errors=errors,
                                  decode_responses=decode_responses, retry_on_timeout=retry_on_timeout,
                                  ssl=ssl, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
                                  ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_certs,
                                  max_connections=max_connections)

    def get_client(self):
        return self.client

    def __del__(self):
        self.close()

    def close(self):
        try:
            del self.client
        except:
            pass


class SQL():
    """
    https://pypi.org/project/python-sql/
    :argument:
        sort_field: 参数排序字段
        page_num: 参数页数
        page_size: 参数页数容量
    """
    eq_argument = {}
    like_argument = {}
    in_argument = {}
    arguments = {}
    order_argument = {}
    section_argument = {}

    def __init__(self):
        self.page_size = self.arguments.get("page_size", 10)
        self.page_num = self.arguments.get("page_num", 1)

    def deal_sql(self, sql_obj):
        s = tuple(sql_obj)
        sql_, value = s[0], s[1]
        sql_ = sql_ % value
        return str(sql_).replace("\"", "")

    @property
    def where_eq_arguments(self):
        out = None
        for k, v in self.eq_argument.items():
            arg = self.arguments.get(k)
            if arg == None:
                continue
            if out == None:
                out = (v == f"'{arg}'")
            else:
                out = out & (v == f"'{arg}'")
        return out

    @property
    def where_like_arguments(self):
        out = None
        for k, v in self.like_argument.items():
            arg = self.arguments.get(k)
            if arg == None:
                continue
            if out == None:
                out = (v.like(f"'%{arg}%'"))
            else:
                out = out & (v.like(f"'%{arg}%'"))
        return out

    @property
    def where_in_arguments(self):
        out = None
        for k, v in self.in_argument.items():
            arg = self.arguments.get(k)
            if arg == None or not arg:
                continue
            args = []
            for i in arg:
                args.append(f"'{i}'")
            if out == None:
                out = (v.in_(args))
            else:
                out = out & (v.in_(args))
        return out

    @property
    def where_section_arguments(self):
        out = None
        for k, v in self.section_argument.items():
            arg = self.arguments.get(k, [])
            if type(arg) != list or len(arg) != 2:
                continue
            if not arg:
                continue
            args1 = arg[0]
            args2 = arg[1]
            if out == None:
                out = (v >= f"'{args1}'") & (v <= f"'{args2}'")
            else:
                out = out & (v >= f"'{args1}'") & (v <= f"'{args2}'")
        return out

    @property
    def where(self):
        out = None
        if self.where_eq_arguments:
            out = self.where_eq_arguments
        if self.where_like_arguments:
            if out:
                out = out & self.where_like_arguments
            else:
                out = self.where_like_arguments
        if self.where_in_arguments:
            if out:
                out = out & self.where_in_arguments
            else:
                out = self.where_in_arguments
        if self.where_section_arguments:
            if out:
                out = out & self.where_section_arguments
            else:
                out = self.where_section_arguments
        return out

    @property
    def order(self):
        ASC = False
        sort_field = self.arguments.get("sort_field")
        if "-" in sort_field:
            name = sort_field[1:]
            ASC = True
        else:
            name = sort_field
        obj = self.order_argument.get(name)
        if obj:
            if ASC:
                return Asc(obj)
            else:
                return obj
        return None

    def reset_page_size(self, page_size=2000):
        self.page_size = page_size

    @property
    def limit(self):
        return self.page_size

    @property
    def offset(self):
        return (self.page_num - 1) * self.page_size

    @property
    def count(self):
        return Count(Literal(1)).as_("count")

    def split_columns_values(self, data: dict):
        """
        字典拆分数据为键值对
        :param data:
        :return:
        """
        cs = []
        vs = []
        for k, v in data.items():
            cs.append(k)
            vs.append(f"'{v}'")

        return cs, vs


class MySQLDB():
    conf_mysql = {}

    def __init__(self, host=None, port=3306, user="root", password="123456", db="test",
                 ssl_ca="", ssl_cert="", ssl_key="",
                 cursorclass="pymysql.cursors.SSCursor"):
        self.db_mysql = self.conf_mysql.get("db", db)
        cursorclass = eval(self.conf_mysql.get("cursorclass", cursorclass))
        ssl_ca = self.conf_mysql.get("ssl_ca", ssl_ca)
        ssl_cert = self.conf_mysql.get("ssl_cert", ssl_cert)
        ssl_key = self.conf_mysql.get("ssl_key", ssl_key)
        if ssl_ca:
            ssl = {"ssl": {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}}
        else:
            ssl = None
        self.connect_args = {"host": self.conf_mysql.get("host", host),
                             "port": int(self.conf_mysql.get("port", port)),
                             "passwd": self.conf_mysql.get("password", password),
                             "user": user,
                             "ssl": ssl,
                             "cursorclass": eval(self.conf_mysql.get("cursorclass", cursorclass))}
        # self.connect(**self.connect_args)
        self.cursor = None
        self.client = None

    def connect(self, **connect_args):
        try:
            self.client = pymysql.connect(**connect_args)
            self.cursor = self.client.cursor()
            self.client.select_db(self.db_mysql)
        except Exception as e:
            raise Exception("---Connect MysqlServer Error--- [%s]" % str(e))

    @staticmethod
    def connect_again(func):
        def wrapper(self, *args, **kwargs):
            if self.cursor == None:
                self.connect(**self.connect_args)
            return func(*args, **kwargs)

        return wrapper

    def execute(self, sql=None):
        if self.cursor == None:
            self.connect(**self.connect_args)
        self.cursor.execute(sql)

    def read_all(self):
        if self.cursor == None:
            self.connect(**self.connect_args)
        return list(self.cursor.fetchall())

    def read_many(self, size):
        if self.cursor == None:
            self.connect(**self.connect_args)
        while True:
            result = list(self.cursor.fetchmany(size=size))
            if not result:
                break
            yield result

    def read_one(self):
        if self.cursor == None:
            self.connect(**self.connect_args)
        while True:
            result = list(self.cursor.fetchone())
            if not result:
                break
            yield result

    def commit(self):
        """commit insert sql"""
        self.client.commit()

    def rollback(self):
        """commit insert sql"""
        self.client.rollback()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        try:
            self.cursor.close()
        except Exception as e:
            pass
        try:
            self.client.close()
        except Exception as e:
            pass
        self.cursor = None
        self.client = None

    def output(self, arg):
        logging.exception(str(arg))

    def create_database(self):
        if self.cursor == None:
            self.connect(**self.connect_args)
        try:
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % self.db_mysql)
        except Exception as e:
            pass


class RandomString():
    def get_hashid(self, min_length=16, salt="PAND"):
        """
        生成随机加密字符串
        :param salt:
        :return:
        """
        ts = int(time.time() * 10000000)
        num = int(shortuuid.ShortUUID(alphabet='0123456789').random(length=8))
        hashids_ = Hashids(min_length=min_length, salt=salt)
        hashid = hashids_.encode(ts, num)
        return hashid

    def get_md5(self, s):
        m = hashlib.md5()
        b = s.encode(encoding='utf-8')
        m.update(b)
        str_md5 = m.hexdigest()
        return str_md5


class MySQLCrud(SQL, MySQLDB, RandomString):
    conf = config.get("mysql", {})

    def __init__(self, **kwargs):
        super(MySQLDB, self).__init__(**kwargs)
        super(SQL, self).__init__()
        super(RandomString, self).__init__()

    def dealer(self):
        pass

    def run(self):
        try:
            data = self.dealer()
            try:
                self.commit()
            except:
                pass
            try:
                self.close()
            except:
                pass
        except Exception as e:
            try:
                self.rollback()
            except:
                pass
            try:
                self.close()
            except:
                pass
            raise e
        return data


class TokenCrud(RandomString):
    conf_redis = config.get("redis", {})
    token_expire = config.get("token", {})

    def __init__(self, args=None, **kwargs):
        super(RandomString, self).__init__()

        self.access_expire = int(self.token_expire.get("access_expire", 180))
        self.fresh_expire = int(self.token_expire.get("fresh_expire", 24 * 60 * 60 * 1))
        self.client = RedisDB(host=self.conf_redis.get("host"), port=int(self.conf_redis.get("port")),
                              password=self.conf_redis.get("password"), db=int(self.conf_redis.get("db"))).client
        self.arguments = kwargs.get("arguments", {})
        if not self.arguments:
            self.arguments = kwargs.get("condition", {})
        self.kwargs = kwargs
        self.args = args

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        self.client.set(name=name, value=value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, name):
        return self.client.get(name=name)

    def delete(self, names: list):
        self.client.delete(*names)

    def keys(self, pattern: str):
        return self.client.keys(pattern=pattern)

    def token_encode(self, enc_json_data, SECRET, user_id, app_id):
        payload = {
            "data": enc_json_data,
            "user_id": user_id,
            "app_id": app_id,
            "timestamp": time.time() + random.randint(1, 10000)
        }
        return self.__token__(payload=payload, SECRET=SECRET)

    def __token__(self, payload: dict, SECRET: str):
        token = jwt.encode(payload, SECRET, algorithm='HS256')
        return token.decode()

    def token_decode(self, token, SECRET):
        decoded = jwt.decode(token.encode(), SECRET, algorithms='HS256')
        return decoded

    def random_string(self):
        m = hashlib.md5()
        m.update(str(time.time()).encode('utf-8'))
        return m.hexdigest()


class NoneCrud(RandomString):
    def __init__(self):
        super(RandomString, self).__init__()

    def dealer(self):
        pass

    def run(self):
        data = self.dealer()
        return data


class Business(TokenCrud):
    backend_params = {
        "url": "http://192.168.1.2:15001/graphql/",
        "method": "post",
        "headers": {"Content-Type": "application/json"}
    }

    # backend_params = {
    #
    # }

    class Argument:
        args = graphene.JSONString(description="json字符串作为参数:例如，{\"query\":\"xxx\",\"variables\":\"xxx\"}")

    class Return:
        ret = graphene.JSONString(description="json字符串作为返回值")

    def validate_graphql_api(self, name):
        try:
            args = self.arguments.get("condition", {}).get("args", {})
            graphql = args.get("query", args.get("mutation", ""))
            pattern = re.compile(r"\(.+?\)")
            graphql = pattern.sub("", graphql)
            graphql = graphql.replace("query ", "").replace("mutation ", "")
            api_name = graphql.split("{")[1].replace("↵", "").strip()
            if api_name != name:
                raise Exception("传入参数与接口不一致")
        except Exception as e:
            # logging.exception(str(e))
            raise Exception("传入参数与接口不一致")

    def validate_token(self, info, **kwargs):
        # try:
        #     token = info.context.get("headers").get("token", "")
        # except:
        #     token = info.context.headers.get("token", "")
        # if not token:
        #     raise Exception("ERROR认证参数为空")
        # names = self.keys(pattern=r"*token:{}".format(token))
        # if names:
        #     property_list = names[0].decode("utf8").split("_")
        #     SECRET = str(self.get(names[0].decode("utf8")).decode("utf8"))
        #     token_info = self.token_decode(token, SECRET)
        #     return {"dec_data": token_info.get("data"), "user_id": token_info.get("user_id")}
        # else:
        #     raise Exception("该token已失效")
        pass

    def validate_privilege(self, token_info, **kwargs):
        pass

    def backend_service(self):
        try:
            response = requests.request(**self.backend_params)
            return response
        except Exception as e:
            raise Exception("请求后端异常：{}".format(str(e)))

class BusinessInfo(TokenCrud):
    def validate_graphql_api(self, name):
        pass
        # try:
        #     args = self.arguments.get("condition", {}).get("args", {})
        #     graphql = args.get("query", args.get("mutation", ""))
        #     pattern = re.compile(r"\(.+?\)")
        #     graphql = pattern.sub("", graphql)
        #     graphql = graphql.replace("query ", "").replace("mutation ", "")
        #     api_name = graphql.split("{")[1].replace("↵", "").strip()
        #     if api_name != name:
        #         raise Exception("传入参数与接口不一致")
        # except Exception as e:
        #     # logging.exception(str(e))
        #     raise Exception("传入参数与接口不一致")

    def validate_token(self, info, **kwargs):
        # try:
        #     token = info.context.get("headers").get("token", "")
        # except:
        #     token = info.context.headers.get("token", "")
        # if not token:
        #     raise Exception("ERROR认证参数为空")
        # names = self.keys(pattern=r"*token:{}".format(token))
        # if names:
        #     property_list = names[0].decode("utf8").split("_")
        #     SECRET = str(self.get(names[0].decode("utf8")).decode("utf8"))
        #     token_info = self.token_decode(token, SECRET)
        #     return {"dec_data": token_info.get("data"), "user_id": token_info.get("user_id")}
        # else:
        #     raise Exception("该token已失效")
        pass

    def validate_privilege(self, token_info, **kwargs):
        pass


class Test(MySQLCrud):
    conf = {
        "host": "117.78.42.21",
        "port": 8050,
        "user": "root",
        "password": "qCqRZJthZe",
        "cursorclass": "pymysql.cursors.SSDictCursor",
        "db": "test1"
    }
    user_group = Table("user_group")
    log = Table("log")
    log1 = Table("log")

    eq_argument = {
        "log_id": log.log_id,
        "log_name": log.log_name
    }
    like_argument = {
        "name": user_group.name
    }

    def dealer(self):
        self.arguments = {"log_id": 1}
        s = self.log.join(self.log1, condition=self.log1.log_id == self.log.log_id)
        a = s.select(self.count, where=self.where)
        sql = self.deal_sql(a)
        self.execute(sql)
        print(self.read_all())
        print(self.read_all())
