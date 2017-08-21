# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space

import datetime
import random
import json
import hashlib


def generate_edit_id():
    """ 唯一编辑ID生成函数 """
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
    edit_id = ''
    for n in time_str:
        edit_id += map_dict[n]
    edit_id += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
    edit_id += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
    edit_id += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
    return edit_id


def manage_del_blog(db, Post, Comment, edit_id):
    """ 删除博文 """
    if edit_id:
        the_blog = Post.query.filter_by(edit_id=edit_id).first()
        if the_blog:
            the_blog_comments = Comment.query.filter_by(post_id=the_blog.id).all()
            db.session.delete(the_blog)
            for comment in the_blog_comments:
                db.session.delete(comment)
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    else:
        return 'error'


def edit_a_blog(db, Post, Tag, request_form, edit_id=None):
    """ 新建或修改博文 """
    if edit_id:
        the_post = Post.query.filter_by(edit_id=edit_id).first()
        if the_post:
            the_post.tags = []
        else:
            return None
    else:
        the_post = Post()
        the_post.edit_id = generate_edit_id()
    the_post.title = request_form.get('title')
    the_post.content = request_form.get('content')
    the_post.post_type = request_form.get('posttype')
    the_post.post_meta = request_form.get('postmeta')
    the_post.post_abstract, the_post.post_content = handle_content(request_form.get('content'))
    the_post.post_status = request_form.get('status')
    the_post.view_type = request_form.get('viewtype')
    if request_form.get('viewpwd'):
        the_post.view_passwd = request_form.get('viewpwd')
    if request_form.get('datetime'):
        the_post.post_time = datetime.datetime.strptime(request_form.get('datetime'), "%Y-%m-%d %H:%M:%S")
    else:
        the_post.post_time = datetime.datetime.now()
    the_post.modified_time = datetime.datetime.now()
    if request_form.get('tags'):
        tags = (request_form.get('tags')).split(',')
        the_post.tags = []
        for n in range(len(tags)):
            the_post.tags.append(Tag.query.filter_by(name=tags[n]).first() or Tag(name=tags[n]))
    if edit_id:
        db.session.commit()
    else:
        db.session.add(the_post)
        db.session.commit()
    return the_post.id


def all_tags_list(Tag):
    """ 查询所有的标签并返回列表 """
    query_all_tag = Tag.query.all()
    all_tags = []
    for n in range(len(query_all_tag)):
        all_tags.append(query_all_tag[n].name)
    return all_tags


def manage_the_tag(db, Tag, request_form):
    """ 标签管理（删除或修改）"""
    if request_form.get('event') == 'modify':
        old_name = request_form.get('old_name')
        new_name = request_form.get('new_name')
        query_tag = Tag.query.filter_by(name=old_name).first()
        if query_tag:
            query_tag.name = new_name
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    elif request_form.get('event') == 'delete':
        tag_name = request_form.get('tag_name')
        query_tag = Tag.query.filter_by(name=tag_name).first()
        if query_tag:
            db.session.delete(query_tag)
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    else:
        return 'error'


def manage_the_comment(db, Comment, request_form):
    """ 评论管理（审阅、回复、删除）"""
    comment_id = request_form.get('comment_id')
    query_comment = Comment.query.filter_by(id=comment_id).first()
    if request_form.get('event') == 'check':
        if query_comment:
            query_comment.comment_check = True
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    elif request_form.get('event') == 'reply':
        reply_content = request_form.get('comment_content')
        if query_comment:
            query_comment.reply = reply_content
            query_comment.reply_time = datetime.datetime.now()
            query_comment.comment_check = True
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    elif request_form.get('event') == 'delete':
        if query_comment:
            db.session.delete(query_comment)
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    else:
        return 'error'


def manage_the_message(db, Message, request_form):
    """ 留言管理（审阅、回复、删除）"""
    message_id = request_form.get('message_id')
    query_message = Message.query.filter_by(id=message_id).first()
    if request_form.get('event') == 'check':
        if query_message:
            query_message.message_check = True
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    elif request_form.get('event') == 'reply':
        reply_content = request_form.get('message_content')
        if query_message:
            query_message.reply = reply_content
            query_message.reply_time = datetime.datetime.now()
            query_message.message_check = True
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    elif request_form.get('event') == 'delete':
        if query_message:
            db.session.delete(query_message)
            db.session.commit()
            return 'ok'
        else:
            return 'error'
    else:
        return 'error'


def manage_the_admin(db, Option, request_form):
    """ 管理员资料管理 """
    if request_form.get('event') == 'get':
        admin_name = (Option.query.filter_by(option_name='admin_name').first()).option_value
        admin_nickname = (Option.query.filter_by(option_name='admin_nickname').first()).option_value
        admin_email = (Option.query.filter_by(option_name='admin_email').first()).option_value
        admin_gravatar = hashlib.md5((admin_email.lower()).encode(encoding='utf-8')).hexdigest()
        return json.dumps({'event': 'ok',
                           'admin_name': admin_name,
                           'admin_nickname': admin_nickname,
                           'admin_email': admin_email,
                           'admin_gravatar': admin_gravatar}, ensure_ascii=False)
    elif request_form.get('event') == 'set':
        admin_name = Option.query.filter_by(option_name='admin_name').first()
        admin_nickname = Option.query.filter_by(option_name='admin_nickname').first()
        admin_email = Option.query.filter_by(option_name='admin_email').first()
        admin_name.option_value = request_form.get('admin_name')
        admin_nickname.option_value = request_form.get('admin_nickname')
        admin_email.option_value = request_form.get('admin_email')
        if request_form.get('old_pwd'):
            admin_pwd = Option.query.filter_by(option_name='admin_pwd').first()
            form_old_pwd = hashlib.sha256(request_form.get('old_pwd').encode(encoding='utf-8')).hexdigest()
            if form_old_pwd == admin_pwd.option_value:
                admin_pwd.option_value = hashlib.sha256(
                    request_form.get('new_pwd').encode(encoding='utf-8')).hexdigest()
            else:
                return json.dumps({'event': 'pwderror'}, ensure_ascii=False)
        db.session.commit()
        return json.dumps({'event': 'ok'}, ensure_ascii=False)
    else:
        return json.dumps({'event': 'error'}, ensure_ascii=False)


def handle_content(content):
    tmp_content = content[:]
    if tmp_content.find('<p><del>这是摘要分隔标签,不会在实际内容中显示</del></p>') >= 0:
        handle_result = tmp_content.split('<p><del>这是摘要分隔标签,不会在实际内容中显示</del></p>')
        add_abstract_info = '<p style="margin: -1.4em 0 0 0;"><strong><span style="font-size: 20px;">. . . . . .</span></strong></p>'
        return handle_result[0] + add_abstract_info, handle_result[0] + handle_result[1]
    else:
        return tmp_content, tmp_content
