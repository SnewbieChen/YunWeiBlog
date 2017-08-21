# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space
import datetime
import hashlib
import json
import random


def get_some_posts(Post, post_id, posts_count, admin=False):
    """ 获取指定id博文时间之前的posts_count篇博文 """
    query_some_posts = None
    some_posts = {}
    if post_id > 0:
        the_datetime_query = Post.query.filter_by(id=post_id).first()
        if the_datetime_query:
            the_datetime = the_datetime_query.post_time
            if admin:
                query_some_posts = Post.query.filter(Post.post_time < the_datetime,
                                                     Post.post_status != 'draft').order_by(Post.post_time.desc()).limit(
                    posts_count).all()
            else:
                query_some_posts = Post.query.filter(Post.post_time < the_datetime, Post.view_type != 'private',
                                                     Post.post_status != 'draft').order_by(Post.post_time.desc()).limit(
                    posts_count).all()
    else:
        if admin:
            query_some_posts = Post.query.filter(Post.post_status != 'draft').order_by(Post.post_time.desc()).limit(
                posts_count).all()
        else:
            query_some_posts = Post.query.filter(Post.post_status != 'draft', Post.view_type != 'private').order_by(
                Post.post_time.desc()).limit(posts_count).all()
    if query_some_posts:
        if admin:
            for n in range(len(query_some_posts)):  # 将查询结果转换为Python字典
                some_posts[n] = {
                    'id': query_some_posts[n].id,
                    'title': query_some_posts[n].title,
                    'post_type': query_some_posts[n].post_type,
                    'post_status': query_some_posts[n].post_status,
                    'view_type': query_some_posts[n].view_type,
                    'view_passwd': query_some_posts[n].view_passwd,
                    'post_time': query_some_posts[n].post_time.strftime("%Y-%m-%d %H:%M"),
                    'modified_time': query_some_posts[n].modified_time.strftime("%Y-%m-%d %H:%M"),
                    'edit_id ': query_some_posts[n].edit_id,
                    'post_meta': query_some_posts[n].post_meta,
                    'post_abstract': query_some_posts[n].post_abstract,
                    'post_content': query_some_posts[n].post_content,
                    'comments': len(query_some_posts[n].comments),
                    'tags': tags_dict(query_some_posts[n].tags)
                }
        else:
            for n in range(len(query_some_posts)):  # 将查询结果转换为Python字典
                if query_some_posts[n].view_type == 'public':
                    some_posts[n] = {
                        'id': query_some_posts[n].id,
                        'title': query_some_posts[n].title,
                        'post_type': query_some_posts[n].post_type,
                        'view_type': query_some_posts[n].view_type,
                        'post_time': query_some_posts[n].post_time.strftime("%Y-%m-%d %H:%M"),
                        'modified_time': query_some_posts[n].modified_time.strftime("%Y-%m-%d %H:%M"),
                        'post_meta': query_some_posts[n].post_meta,
                        'post_abstract': query_some_posts[n].post_abstract,
                        'post_content': query_some_posts[n].post_content,
                        'comments': len(query_some_posts[n].comments),
                        'tags': tags_dict(query_some_posts[n].tags)
                    }
                elif query_some_posts[n].view_type == 'encrypt':
                    some_posts[n] = {
                        'id': query_some_posts[n].id,
                        'title': query_some_posts[n].title,
                        'post_type': query_some_posts[n].post_type,
                        'view_type': query_some_posts[n].view_type,
                        'post_time': query_some_posts[n].post_time.strftime("%Y-%m-%d %H:%M"),
                        'modified_time': query_some_posts[n].modified_time.strftime("%Y-%m-%d %H:%M"),
                        'comments': len(query_some_posts[n].comments),
                        'tags': tags_dict(query_some_posts[n].tags)
                    }
    else:
        some_posts = None
    return some_posts


def get_the_post(Post, post_id, admin=False):
    """ 获取指定id的博文 """
    if admin:
        the_post_query = Post.query.filter_by(id=post_id).first()
    else:
        the_post_query = Post.query.filter(Post.post_status != 'draft',
                                           Post.view_type != 'private', Post.id == post_id).first()
    return the_post_query


def do_blog_comment(db, Post, Comment, request_form, client_ip):
    """ 发表博客评论 """
    if request_form.get('post_id'):
        blog_query = Post.query.filter(Post.post_status != 'draft', Post.id == request_form.get('post_id')).first()
        if blog_query:
            the_comment = Comment()
            the_comment.post_id = request_form.get('post_id')
            the_comment.author_name = request_form.get('author_name')
            the_comment.author_email = request_form.get('author_email')
            the_comment.content = request_form.get('comment_content')
            the_comment.author_ip = client_ip
            the_comment.post_time = datetime.datetime.now()
            db.session.add(the_comment)
            db.session.commit()
            author_gravatar = hashlib.md5(
                (request_form.get('author_email').lower()).encode(encoding='utf-8')).hexdigest()
            return json.dumps({'event': 'ok',
                               'author_time': the_comment.post_time.strftime("%Y-%m-%d %H:%M"),
                               'author_gravatar': author_gravatar}, ensure_ascii=False)
        else:
            return json.dumps({'event': 'error'}, ensure_ascii=False)
    else:
        return json.dumps({'event': 'error'}, ensure_ascii=False)


def check_view_pwd(db, Post, Option, request_form):
    """ 检查查看密码 """
    post_id = request_form.get('post_id')
    view_pwd = request_form.get('view_pwd')
    if post_id:
        the_post_query = Post.query.filter_by(id=post_id).first()
        if the_post_query:
            if the_post_query.view_passwd == view_pwd:
                view_id = generate_view_id()
                option_view_id = Option(option_name=view_id, option_value=post_id)
                db.session.add(option_view_id)
                db.session.commit()
                return '/secret/' + view_id
            else:
                return 'error'
        else:
            return 'error'
    else:
        return 'error'


def get_secret_post(db, Post, Option, view_id):
    """ 获取加密博文 """
    if view_id:
        the_view_id_query = Option.query.filter_by(option_name=view_id).first()
        if the_view_id_query:
            the_post_query = Post.query.filter_by(id=the_view_id_query.option_value).first()
            db.session.delete(the_view_id_query)
            db.session.commit()
            return the_post_query
        else:
            return None
    else:
        return None


def get_tag_posts(Tag, tag_name):
    """ 获取指定标签的博文 """
    query_tag = Tag.query.filter_by(name=tag_name).first()
    if query_tag:
        return query_tag.posts
    else:
        return None


def get_view_posts_map(Post, admin=False):
    """ 获取文章时间归档 """
    time_line_posts = {}
    if admin:
        query_all_posts = Post.query.filter(Post.post_status != 'draft').order_by(Post.post_time.desc()).all()
    else:
        query_all_posts = Post.query.filter(Post.post_status != 'draft', Post.view_type != 'private').order_by(
            Post.post_time.desc()).all()
    for n in range(len(query_all_posts)):
        if query_all_posts[n].post_time.year not in time_line_posts:
            time_line_posts[query_all_posts[n].post_time.year] = {}
        if query_all_posts[n].post_time.month not in time_line_posts[query_all_posts[n].post_time.year]:
            time_line_posts[query_all_posts[n].post_time.year][query_all_posts[n].post_time.month] = {}
            line_mini_count = 0
        else:
            line_mini_count += 1
        time_line_posts[query_all_posts[n].post_time.year][query_all_posts[n].post_time.month][line_mini_count] = {
            'id': query_all_posts[n].id,
            'title': query_all_posts[n].title,
            'post_type': query_all_posts[n].post_type,
            'view_type': query_all_posts[n].view_type,
            'comments': len(query_all_posts[n].comments),
            'post_day': query_all_posts[n].post_time.strftime("%d")}
    return time_line_posts


def get_view_tag_map(Tag):
    query_all_tag = Tag.query.all()
    all_tag = {}
    for n in range(len(query_all_tag)):
        all_tag[query_all_tag[n].name] = len(query_all_tag[n].posts)
    return all_tag


def do_message(db, Message, request_form, client_ip):
    """ 发表留言 """
    the_message = Message()
    the_message.author_name = request_form.get('author_name')
    the_message.author_email = request_form.get('author_email')
    the_message.message = request_form.get('message')
    the_message.author_ip = client_ip
    the_message.post_time = datetime.datetime.now()
    db.session.add(the_message)
    db.session.commit()
    author_gravatar = hashlib.md5(
        (request_form.get('author_email').lower()).encode(encoding='utf-8')).hexdigest()
    return json.dumps({'event': 'ok',
                       'author_time': the_message.post_time.strftime("%Y-%m-%d %H:%M"),
                       'author_gravatar': author_gravatar},
                      ensure_ascii=False)


def tags_dict(tags_obj):
    """ 将标签查询结果转换为Python字典 """
    tmp_obj = {}
    if tags_obj:
        for n in range(len(tags_obj)):
            tmp_obj[n] = tags_obj[n].name
        return tmp_obj
    else:
        return None


def generate_view_id():
    """ 唯一查看ID生成函数 """
    map_dict = {'0': random.choice('0co'),
                '1': random.choice('1dp'),
                '2': random.choice('2eq'),
                '3': random.choice('3fr'),
                '4': random.choice('4gs'),
                '5': random.choice('5ht'),
                '6': random.choice('6iu'),
                '7': random.choice('7jv'),
                '8': random.choice('8kw'),
                '9': random.choice('9lx'),
                '-': random.choice('amy'),
                ':': random.choice('bnz')}
    time_str = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    view_id = ''
    for n in time_str:
        view_id += map_dict[n]
    view_id += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
    view_id += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
    view_id += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
    return view_id
