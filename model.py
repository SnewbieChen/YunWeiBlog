# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 博文与标签的多对多关系表
post_tags = db.Table('post_tags', db.Model.metadata,
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                     )


class Post(db.Model):
    """
    博客文章数据库表
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))  # 文章标题
    content = db.Column(db.Text)  # 输入正文
    post_type = db.Column(db.String(64))  # 文章类型（文章、代码、照片、图集、音乐、视频）[article、code、photo、album、music、video]
    post_status = db.Column(db.String(64), index=True)  # 发表状态（草稿、发布）[draft、published]
    view_type = db.Column(db.String(64), index=True)  # 查看类型（公开、仅自己可看、密码查看）[public、private、encrypt]
    view_passwd = db.Column(db.String(64))  # 加密密码（仅加密文章适用）
    post_time = db.Column(db.DateTime, index=True)  # 发布时间
    modified_time = db.Column(db.DateTime)  # 修改时间
    edit_id = db.Column(db.String(64), index=True, unique=True)  # 编辑链接id
    post_meta = db.Column(db.Text)  # 文章元数据头
    post_abstract = db.Column(db.Text)  # 文章摘要
    post_content = db.Column(db.Text)  # 文章正文
    comments = db.relationship('Comment', backref='post', order_by='Comment.post_time.desc()')  # 评论关系
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts', order_by='Post.post_time.desc()'))  # 标签关系


class Tag(db.Model):
    """
    文章标签数据库表
    """
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)  # 标签名


class Comment(db.Model):
    """
    文章评论数据库表
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))  # 文章ID
    author_name = db.Column(db.String(64))  # 评论者名称
    author_email = db.Column(db.String(64))  # 评论者的Email
    author_ip = db.Column(db.String(64))  # 评论者的IP
    post_time = db.Column(db.DateTime)  # 评论时间
    content = db.Column(db.Text)  # 评论内容
    reply_time = db.Column(db.DateTime)  # 回复时间
    reply = db.Column(db.Text)  # 回复内容
    comment_check = db.Column(db.Boolean, index=True, default=False)  # 评论已检查


class File(db.Model):
    """
    博客附件数据库表
    """
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))  # 文件标示名
    type = db.Column(db.String(64), index=True)  # 文件类型（图片、视频、其他）[photo、video、file]
    upload_time = db.Column(db.DateTime)  # 上传时间
    url = db.Column(db.String(128), index=True)  # 文件相对url
    thumbnail_url = db.Column(db.String(128))  # 图片缩略图相对url


class Option(db.Model):
    """
    博客参数数据库表
    """
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    option_name = db.Column(db.String(64), unique=True, index=True)  # 配置项
    option_value = db.Column(db.String(255))  # 参数值


class Message(db.Model):
    """
    留言数据库表
    """
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(64))  # 留言中名称
    author_email = db.Column(db.String(64))  # 留言者Email
    author_ip = db.Column(db.String(64))  # 留言者的IP
    post_time = db.Column(db.DateTime)  # 留言时间
    message = db.Column(db.Text)  # 留言内容
    reply_time = db.Column(db.DateTime)  # 回复时间
    reply = db.Column(db.Text)  # 回复内容
    message_check = db.Column(db.Boolean, index=True, default=False)  # 留言已检查
