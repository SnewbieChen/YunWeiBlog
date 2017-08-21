# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space

import os
import datetime


class Config:
    DEBUG = False  # 是否开启调试模式
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://yunwei:chen@yunwei#space@localhost/myspace'  # 数据库URI
    SECRET_KEY = 'Chen@YunWei#Space->Blog'  # session加密密钥
    JSON_AS_ASCII = False  # 让JSON字符串显示中文
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=3)  # 设置session过期时间为3天
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    UPLOAD_DIR = 'uploads'  # 文件保存文件夹名
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_DIR)  # 文件上传目录

