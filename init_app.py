# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space

import hashlib
from flask import Flask
from config import Config
from model import db, Option

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
db.app = app
db.drop_all()
db.create_all()

domain_name = 'chen.yunwei.space'
admin_name = 'yunwei'
admin_nickname = '云炜'
admin_email = 'snewbie@163.com'
base_pwd = '123456'

admin_pwd = hashlib.sha256(base_pwd.encode(encoding='utf-8')).hexdigest()
option_domain_name = Option(option_name='domain_name', option_value=domain_name)
option_admin_name = Option(option_name='admin_name', option_value=admin_name)
option_admin_nickname = Option(option_name='admin_nickname', option_value=admin_nickname)
option_admin_email = Option(option_name='admin_email', option_value=admin_email)
option_admin_pwd = Option(option_name='admin_pwd', option_value=admin_pwd)

db.session.add(option_domain_name)
db.session.add(option_admin_name)
db.session.add(option_admin_nickname)
db.session.add(option_admin_email)
db.session.add(option_admin_pwd)

db.session.commit()
