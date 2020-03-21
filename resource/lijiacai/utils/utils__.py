#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""
import decimal
import os
import random
import sys
import json
import time
import redis
import pymysql
import configparser
import jwt
import hashlib
import casbin_sqlalchemy_adapter
import casbin
import functools
import shortuuid
import logging
import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import aliased
import datetime
from sqlalchemy import create_engine, Table
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import text
from sqlalchemy.sql.selectable import Alias
from sqlalchemy import func
from hashids import Hashids


def get_config(conf_file="./configure/main.conf"):
    config = configparser.ConfigParser()
    config.read(conf_file)
    info = config._sections
    return info


class SqlDBOrm():
    """
    # >>> host = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8"
    # >>> mysql = SqlDBOrm(host)
    # >>> baseClass = mysql.get_modelClass()
    # >>> Stations = baseClass.stations
    # # sql查询
    # >>> data = session.execute(sql="select * from customers;")
    # >>> data = list(data.fetchall())
    # >>> print(data)
    # # orm查询
    # >>> session = mysql.get_session()
    # >>> condition = [Stations.id==1]
    # >>> with mysql.session_maker(session) as sess:
    # >>> ... res = sess.query(Stations).filter(*condition).all()
    # >>> ... for station in res:
    # >>> ...         result = mysql.attr_to_dict(station)
    # >>> ...         print(result)

    """

    def __init__(self, host="mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8",
                 poolclass=NullPool, ssl_ca="", ssl_cert="", ssl_key=""):
        connect_args = {}
        if ssl_ca:
            connect_args["ssl"] = {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}
        # if cursorclass:
        #     connect_args["cursorclass"] = cursorclass
        # if not connect_args:
        #     connect_args = None
        self.engine = create_engine(host,
                                    poolclass=poolclass, connect_args=connect_args
                                    )
        try:
            from sqlalchemy import MetaData
            # Base = declarative_base()
            metadata = MetaData(self.engine)
            # Base.metadata.reflect(self.engine, views=True)
            metadata.reflect(self.engine, views=True)
            # print(Base.metadata.__dir__())
            # tables = Base.metadata.tables
            # # # print(Base.metadata.mapped_keys())
            # print(tables.keys())
            # print(type(tables["user_group_view"]))
            # print(metadata.tables.keys())
            Base = automap_base(metadata=metadata)
            Base.prepare()
            # print(Base.__dict__)
            self.modelClass = Base.classes
            # print(self.modelClass)
        except Exception as e:
            logging.exception(e)

        # print(self.modelClass.user_group_view)
        self.session = Session(self.engine)

        # user_group = Table('user_group', Base.metadata, autoload=True, autoload_with=self.engine)
        # session = Session(self.engine)
        #
        # '''反射数据库所有的表
        # Base = automap_base()
        # Base.prepare(engine, reflect=True)
        # Admin = Base.classes.admin
        # '''
        # try:
        #     res = session.add(user_group(**{
        #     "plat": "test"
        # }))
        # except Exception as e:
        #     logging.exception(e)

        # print(res.user_group_id)

    @property
    def get_modelClass(self):
        return self.modelClass

    @property
    def get_session(self):
        return Session(self.engine)

    def close(self):
        try:
            self.session.close()
        except:
            pass

    def __del__(self):
        self.close()

    @staticmethod
    @contextmanager
    def session_maker(session=None):
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def attr_to_dict(model):
        dic = dict()
        for c in model.__table__.columns:
            k = c.name
            v = getattr(model, c.name)
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
                dic[k] = v
            elif isinstance(v, decimal.Decimal):
                dic[k] = float(v)
            else:
                dic[k] = v
        return dic


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


import pymysql


class CreateSQL():
    def select_from_where(self, tables: list, fields=None, wheres=None, groups=None, orders=None, limit=10, offset=0):
        """

        :param tables:  ["log","user"]
        :param fields:  ["log.id","user.*"]
        :param wheres:  ["log.id=user.id"]
        :param groups:  ["log.id"]
        :param orders:  ["log.time DESC"]
        :param limit:   10
        :param offset:  0
        :return:
        """
        if fields == None:
            fields = ["*"]
            # for t in tables:
            #     fields.append(f"{t}.*")
        sql = f"SELECT {','.join(fields)} FROM {','.join(tables)} "
        if wheres:
            sql += f" WHERE "
            sql += " AND ".join(wheres)
        sql = self.group_order_limit_offset(sql=sql, groups=groups, orders=orders, limit=limit, offset=offset)
        self.sql = sql
        return sql

    def select_from_join_where(self, tables: list, join_tables: list, fields=None, wheres=None, groups=None,
                               orders=None, limit=None, offset=0):
        """

        :param tables:
        :param join_tables:
        :param fields:
        :param wheres:
        :param groups:
        :param orders:
        :param limit:
        :return:
        """
        if fields == None:
            fields = ["*"]
        tables = tables + join_tables
        sql = f"SELECT {','.join(fields)} FROM {','.join(tables)} "
        if wheres:
            sql += f" WHERE "
            sql += " AND ".join(wheres)
        sql = self.group_order_limit_offset(sql=sql, groups=groups, orders=orders, limit=limit, offset=offset)
        self.sql = sql
        return sql

    def group_order_limit_offset(self, sql, groups=None,
                                 orders=None, limit=None, offset=None):
        if groups:
            sql += " GROUP BY "
            sql += ",".join(groups)
        if orders:
            sql += " ORDER BY "
            sql += ",".join(orders)
        if limit != None:
            sql += f" LIMIT {limit} "
        if offset != None:
            sql += f" OFFSET {offset} "
        return sql

    def add(self, table: str, data: dict, field_filter=None):
        field_names = []
        field_values = []
        if field_filter == None:
            field_names = data.keys()
        else:
            field_names = field_filter
        for k in field_names:
            field_values.append("'{}'".format(str(data.get(k))))
        sql = f"INSERT INTO {table} ({','.join(field_names)}) VALUES ({','.join(field_values)})"
        sql = sql.replace("'None'", "NULL")
        self.sql = sql
        return sql

    def add_all(self, table: str, datas: list, field_filter: list):
        field_names = field_filter
        sql = f"INSERT INTO {table} ({','.join(field_names)}) VALUES "
        field_values_list = []
        for data in datas:
            field_values = []
            for k in field_names:
                field_values.append("'{}'".format(str(data.get(k))))
            field_values_list.append(f"({','.join(field_values)})")
        sql += f"{','.join(field_values_list)}"
        sql = sql.replace("'None'", "NULL")
        self.sql = sql
        return sql

    def update(self, table: str, data: dict, wheres=None):
        if wheres == None:
            wheres = []
        values = []
        for k, v in data.items():
            if type(v) == str:
                values.append(f"{k}='{v}'")
            else:
                values.append(f"{k}={v}")
        sql = f"UPDATE {table} SET {''.join(values)} "
        if wheres:
            sql += f"WHERE {' AND '.join(wheres)}"

    def update_by_in(self, table: str, data: dict, in_: list, in_filed="id"):
        values = []
        in_s = []
        for k, v in data.items():
            if type(v) == str:
                values.append(f"{k}='{v}'")
            else:
                values.append(f"{k}={v}")
        for i in in_:
            if type(i) == str:
                in_s.append(f"'{i}'")
            else:
                in_s.append(str(i))
        sql = f"UPDATE {table} SET {''.join(values)} "
        if in_:
            sql += f"WHERE {in_filed} in ({','.join(in_s)})"
        self.sql = sql
        return sql

    def delete(self, table: str, wheres=None):
        if wheres == None:
            wheres = []

        sql = f"DELETE FROM {table} "
        if wheres:
            sql += f"WHERE {' AND '.join(wheres)}"
        self.sql = sql
        return sql

    def delete_by_in(self, table: str, in_: list, in_filed="id"):
        sql = f"DELETE FROM {table} "
        in_s = []
        for i in in_:
            if type(i) == str:
                in_s.append(f"'{i}'")
            else:
                in_s.append(str(i))
        if in_:
            sql += f"WHERE {in_filed} in ({','.join(in_s)})"
        self.sql = sql
        return sql


class MySQLDB(CreateSQL):
    conf = {
        "host": "117.78.42.21",
        "port": 8050,
        "user": "root",
        "password": "qCqRZJthZe",
        "db": "test1",
        "cursorclass": "pymysql.cursors.SSDictCursor"
    }

    def __init__(self, host=None, port=3306, user="root", password="123456", db="test",
                 ssl_ca="", ssl_cert="", ssl_key="",
                 cursorclass="pymysql.cursors.SSCursor"):
        self.db = self.conf.get("db", db)
        host = self.conf.get("host", host)
        port = int(self.conf.get("port", port))
        user = self.conf.get("user", user)
        password = self.conf.get("password", password)
        cursorclass = eval(self.conf.get("cursorclass", cursorclass))
        ssl_ca = self.conf.get("ssl_ca", ssl_ca)
        ssl_cert = self.conf.get("ssl_cert", ssl_cert)
        ssl_key = self.conf.get("ssl_key", ssl_key)
        if ssl_ca:
            ssl = {"ssl": {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}}
        else:
            ssl = None
        try:
            self.client = pymysql.connect(host=host, port=port, passwd=password, user=user,
                                          ssl=ssl,
                                          cursorclass=cursorclass)
            self.cursor = self.client.cursor()
            self.client.select_db(self.db)
        except Exception as e:
            raise Exception("---Connect MysqlServer Error--- [%s]" % str(e))

    def execute(self, sql=None):
        if sql == None:
            sql = self.sql
        self.cursor.execute(sql)

    def read_all(self):
        return list(self.cursor.fetchall())

    def read_many(self, size):
        while True:
            result = list(self.cursor.fetchmany(size=size))
            if not result:
                break
            yield result

    def read_one(self):
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

    def output(self, arg):
        logging.exception(str(arg))

    def create_database(self):
        try:
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % self.db)
        except Exception as e:
            pass

    def validate_arguments(self):
        pass
        # data = {
        #     "not_null_list": [],
        #     "enum_list": {},
        #     "phone_list": [],
        #     "email_list": [],
        #     "section_time_list": [],
        #     "time_list": []
        # }
        # ValidateTool(**data, **self.arguments)

    def run(self):
        """程序运行入口"""
        try:
            self.validate_arguments()
            data = self.dealer()
            self.commit()
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

    def dealer(self):
        """处理器,用户需要这里自行定义逻辑"""
        # data = {"city_code": "40000"}
        # res = self.orm_add(model_name="pd_city_area", data=data)
        # datas = [{"city_code": "50000"}, {"city_code": "60000"}]
        # res = self.orm_add_all(model_name="pd_city_area", datas=datas)
        # update_data = {"city_code": "40000"}
        # res = self.orm_update(model_name="pd_city_area", ids=[1,2], update_data=update_data)
        # res = self.orm_delete(model_name="pd_city_area", ids=[1, 2])
        # print(res)
        # print(self.deal_filter_field())
        # print(self.read())
        pass


config = get_config()
mysql = SqlDBOrm(host=config.get("orm").get("host"))
session = mysql.get_session
model = mysql.get_modelClass
# print(model.keys())
for m in model.__dir__():

    if m[0] == "_":
        continue
    # exec("{} = model['{}']".format(m, m))
    # print(eval(f"{m}").__dir__())
    exec("{} = model.{}".format(m, m))
    for i in range(1, 2 + 1):
        exec("{}_{} = aliased({})".format(m, i, m))


def deal_map_code():
    out = {}
    # with mysql.session_maker(session) as sess:
    #     res = sess.query(eval("system_code_map")).filter().all()
    #     for info in res:
    #         result = mysql.attr_to_dict(info)
    #         out[result.get("key")] = result.get("value")
    # return out
    return out


map_code = deal_map_code()


#######


class TokenCrud():
    def __init__(self, args=None, **kwargs):
        cont = config.get("redis", {})
        host = cont.get("host")
        port = int(cont.get("port", 6379))
        db = int(cont.get("db", 0))
        password = cont.get("password")
        token_expire = config.get("token", {})
        self.access_expire = int(token_expire.get("access_expire", 180))
        self.fresh_expire = int(token_expire.get("fresh_expire", 24 * 60 * 60 * 1))
        self.client = RedisDB(host=host, port=port, password=password, db=db).client
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


class OrmCrud():
    """
    *** 主要简化多表联查的情况, 注意每个表都有附表***
    select_model: query模型，传入列表（模型名称）,注意查询ids时，模型列表中的第一个模型作为ids返回值
    select_field: query模型字段，针对只需要某一个字段，传入列表（模型名称.字段）
    subquery: query子查询模型，subquery通过OrmCrud(**kwargs).deal_subquery_model()获取新子查询模型 # 慎用
    outerjoin: 左外连接查询条件，注意模型的先后顺序,完全按照filter()语法，model2.field2 == model1.field1
    filter_eq_arguments: kwargs参数arguments中的字段，需要加入filter进行过滤(等值过滤)
    order_by_arguments: 参数sort_field字段，需要加入排序order_by进行排序
    group_by: 按某字段分组过滤
    special_filter: 特殊过滤条件,完全按照filter()语法，model2.field2 == model1.field1
    True_False_field: 查询的返回字段，进行汉化，例如 0 -- > 否 ，1 --> 是
    map_field: 意思同上，实现返回字段，进行汉化，例如 1000 --> 成功， 1001 --> 失败(映射关系一般来自数据字典)
    样例：
        select_model = ["pd_city", "pd_city_area"]
        select_field = ["pd_city.id", "pd_city.create_time"]
        subquery = []
        outerjoin = {"pd_city_area": ["pd_city.id == pd_city_area.id"]}
        filter_eq_arguments = {"pd_city": ["id"]}
        order_by_arguments = {"create_time": "pd_city"}
        group_by = "pd_city.id"
        special_filter = ["pd_city.id != None"]
        True_False_field = ["is_delete"]
        map_field = ["status"]
    测试用例:
        kwargs = {"arguments": {"id": 1, "creat_time": ["2019-01-01", "2020-01-01"]}, "sort_field": "-create_time"}
        a = OrmCrud(**kwargs).read()
        print(json.dumps(a))
    """
    select_model = []
    select_field = []
    subquery = []
    outerjoin = {}
    filter_eq_arguments = {}
    filter_like_arguments = {}
    filter_in_arguments = {}
    order_by_arguments = {}
    group_by = ""
    special_filter = []
    True_False_field = []
    map_field = []

    def __init__(self, args=None, **kwargs):
        """
        :param args:  用于接受额外其他参数
        :param kwargs: 固定参数
            ｛
                "page_num": 1,
                ""page_size: 10,
                "order_field": "-create_time",
                "arguments": {
                    "city_code": "40000"
                }
            ｝
        """
        self.arguments = kwargs.get("arguments", {})
        self.page_num = kwargs.get("page_num", 1)
        self.page_size = kwargs.get("page_size", 10)
        self.sort_field = kwargs.get("sort_field", {})
        if not self.arguments:
            self.arguments = kwargs.get("condition", {})
        self.kwargs = kwargs
        self.args = args
        self.session = mysql.get_session

    def set_page_size_limit(self, page_num=None, page_size=2000):
        """设置当前查询的最大数量限制"""
        if page_num:
            self.page_num = page_num
        self.page_size = page_size

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

    def attr_to_dict(self, model):
        if not model:
            return {}
        dic = dict()
        for c in model.__table__.columns:
            k = c.name
            v = getattr(model, c.name)
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
                dic[k] = v
            elif isinstance(v, decimal.Decimal):
                dic[k] = float(v)
            elif isinstance(v, datetime.time):
                v = v.strftime("%H:%M:%S")
                dic[k] = v

            elif k in self.True_False_field:
                if v == 0 or v == "0":
                    dic[k] = v
                    dic["{}_value".format(k)] = "否"
                elif v == 1 or v == "1":
                    dic[k] = v
                    dic["{}_value".format(k)] = "是"
                else:
                    dic[k] = v
            elif k in self.map_field:
                if v in map_code:
                    dic[k] = v
                    dic["{}_value".format(k)] = map_code[v]
                else:
                    dic[k] = v
            else:
                dic[k] = v
        return dic

    def field_to_dict(self, *args):
        dic = {}
        for i in range(len(args)):
            k = self.select_field[i]
            v = args[i]
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
                dic[k] = v
            elif isinstance(v, decimal.Decimal):
                dic[k] = float(v)
            elif isinstance(v, datetime.time):
                v = v.strftime("%H:%M:%S")
                dic[k] = v
            elif k in self.True_False_field:
                if v == 0 or v == "0":
                    dic[k] = v
                    dic["{}_value".format(k)] = "否"
                elif v == 1 or v == "1":
                    dic[k] = v
                    dic["{}_value".format(k)] = "是"
                else:
                    dic[k] = v
            elif k in self.map_field:
                if v in map_code:
                    dic[k] = v
                    dic["{}_value".format(k)] = map_code[v]
                else:
                    dic[k] = v
            else:
                dic[k] = v
        return dic

    def subquery_to_dict(self, *args):
        result = []
        for i in range(len(args)):
            v = args[i]
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
                result.append(v)

            elif isinstance(v, decimal.Decimal):
                result.append(float(v))
            elif isinstance(v, datetime.time):
                v = v.strftime("%H:%M:%S")
                result.append(v)
            else:
                result.append(v)
        return {"subquery_result": result}

    def deal_filter(self):
        actions = []
        for k, v in self.filter_eq_arguments.items():
            for one in v:
                if self.arguments.get(one) != None and type(self.arguments.get(one)) != list:
                    actions.append(eval("{}.{}".format(k, one)) == self.arguments.get(one))
                elif self.arguments.get(one) != None and type(self.arguments.get(one)) == list and len(
                        self.arguments.get(one)) == 2:
                    actions.append(eval("{}.{}".format(k, one)) >= self.arguments.get(one)[0])
                    actions.append(eval("{}.{}".format(k, one)) <= self.arguments.get(one)[1])
        for one in self.special_filter:
            if type(one) == str:
                actions.append(eval(one))
            else:
                logging.debug("special_filter error 【{}】".format(one))

        for k, v in self.filter_like_arguments.items():
            for one in v:
                if self.arguments.get(one) != None and type(self.arguments.get(one)) != list:
                    actions.append(eval("{}.{}.like('%{}%')".format(k, one, self.arguments.get(one))))

        for k, v in self.filter_in_arguments.items():
            for one in v:
                if type(self.arguments.get(one)) == list:
                    actions.append(eval("{}.{}".format(k, one)).in_(self.arguments.get(one)))
        return actions

    def deal_order(self):
        for k, v in self.order_by_arguments.items():
            if self.sort_field and type(self.sort_field) == str:
                if self.sort_field[1:] == k:
                    return text("{}{}.{}".format(self.sort_field[0], v, self.sort_field[1:]))
        return text("")

    def deal_select_from(self):
        select_models = []
        select_fields = []
        for select in self.select_model:
            select_models.append(eval(select))
        for select in self.select_field:
            select_fields.append(eval(select))
        return select_models + select_fields + self.subquery

    def deal_outerjoin(self, mid_model):
        for k, v in self.outerjoin.items():
            for c in v:
                mid_model = mid_model.outerjoin(eval(k), eval(c))
        return mid_model

    def deal_group_by(self, mid_model):
        return mid_model.group_by(text(self.group_by))

    def deal_limit_offset(self, mid_model):
        return mid_model.limit(self.page_size).offset(
            (self.page_num - 1) * self.page_size)

    def deal_read_model(self, close_limit=False):
        mid_model = self.session.query(*self.deal_select_from()).filter(*self.deal_filter())
        mid_model = self.deal_outerjoin(mid_model)
        mid_model = self.deal_group_by(mid_model)
        mid_model = mid_model.order_by(self.deal_order())
        if not close_limit:
            mid_model = self.deal_limit_offset(mid_model)
        return mid_model

    def deal_subquery_model(self):
        mid_model = self.session.query(*self.deal_select_from()).filter(*self.deal_filter())
        mid_model = self.deal_outerjoin(mid_model)
        mid_model = self.deal_group_by(mid_model)
        mid_model = mid_model.order_by(self.deal_order()).subquery()
        return mid_model

    def ids(self, field: str):
        """
        :return: 查询的ids
        """
        if not self.select_model:
            raise Exception("查询ids列表，select_model不能为空")
        ids_ = []
        self.delete_data = []
        result = self.read()
        for i in result:
            self.delete_data.append(i[0])
            ids_.append(i[0].get(field))
        return ids_

    @property
    def total(self):
        """
        :return: 查询的数量
        """
        mid_model = self.deal_read_model(close_limit=True)
        return mid_model.count()

    def read(self):
        """读操作"""
        mid_model = self.deal_read_model()
        result = mid_model.all()
        select_model_length = len(self.select_model)
        select_field_length = len(self.select_field)
        subquery_length = len(self.subquery)
        out = []
        for info in result:
            middle = []
            if select_model_length + select_field_length + subquery_length < 2:
                info = [info]
            for model in info[:select_model_length]:
                middle.append(self.attr_to_dict(model))
            if select_field_length:
                middle.append(self.field_to_dict(*info[select_model_length:select_field_length + select_model_length]))
            if subquery_length:
                middle.append(self.subquery_to_dict(*info[select_field_length + select_model_length:]))
            out.append(middle)
        return out

    def add(self, model_name: str, data: dict):
        """添加操作"""
        data = data
        return self.session.add(eval("{}".format(model_name))(**data))

    def add_all(self, model_name: str, datas: list):
        """批量添加操作"""
        if not datas:
            return
        actions = []
        for dic in datas:
            actions.append(eval("{}".format(model_name))(**dic))
        return self.session.add_all(actions)

    def update(self, model_name: str, data_list: list, field: str, update_data: dict):
        """更新操作"""
        return eval(
            "self.session.query(eval(model_name)).filter(eval(model_name).{}.in_(data_list)).update(update_data,synchronize_session=False)".format(
                field))

    def delete(self, model_name: str, data_list: list, field: str):
        """删除操作"""
        return eval(
            "self.session.query(eval(model_name)).filter(eval(model_name).{}.in_(data_list)).delete(synchronize_session=False)".format(
                field))

    def validate_arguments(self):
        pass
        # data = {
        #     "not_null_list": [],
        #     "enum_list": {},
        #     "phone_list": [],
        #     "email_list": [],
        #     "section_time_list": [],
        #     "time_list": []
        # }
        # ValidateTool(**data, **self.arguments)

    def run(self):
        """程序运行入口"""
        try:
            self.validate_arguments()
            data = self.dealer()
            self.session.commit()
        except Exception as e:
            try:
                self.session.rollback()
            except:
                pass
            try:
                self.session.close()
            except:
                pass
            raise e
        return data

    def dealer(self):
        """处理器,用户需要这里自行定义逻辑"""
        # data = {"city_code": "40000"}
        # res = self.orm_add(model_name="pd_city_area", data=data)
        # datas = [{"city_code": "50000"}, {"city_code": "60000"}]
        # res = self.orm_add_all(model_name="pd_city_area", datas=datas)
        # update_data = {"city_code": "40000"}
        # res = self.orm_update(model_name="pd_city_area", ids=[1,2], update_data=update_data)
        # res = self.orm_delete(model_name="pd_city_area", ids=[1, 2])
        # print(res)
        # print(self.deal_filter_field())
        print(self.read())
