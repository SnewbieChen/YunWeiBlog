# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space

from flask import Flask, request, session, redirect, url_for, abort, render_template, jsonify, send_from_directory
from config import Config
from model import db, Post, Comment, Tag, Option, File, Message
from admin import *
from upload import *
from views import *

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
db.app = app


@app.route('/', methods=['GET', 'POST'])
def index():
    """ 主页路由 """
    if 'adminname' in session:
        is_admin = True
    else:
        is_admin = False
    if request.method == 'POST':
        if request.form.get('post_id'):
            some_posts = get_some_posts(Post, int(request.form.get('post_id')), 7, is_admin)  # 获取7篇博文
            if some_posts:
                return jsonify(some_posts)
            else:
                return jsonify({'nomore': 'yes'})
        else:
            abort(404)
    else:
        return render_template('view_index.html')


@app.route('/post/<int:post_id>')
def get_post(post_id):
    """ 获取文章的路由 """
    if 'adminname' in session:
        is_admin = True
    else:
        is_admin = False
    the_post = get_the_post(Post, post_id, is_admin)  # 获取指定id的博文
    if the_post:
        return render_template('view_blog.html', the_post=the_post)
    else:
        abort(404)


@app.route('/tag/<tag_name>')
def get_tag(tag_name):
    """ 获取标签所有文章的路由 """
    tag_posts = get_tag_posts(Tag, tag_name)
    if tag_posts:
        return render_template('view_tag.html', tag_name=tag_name, tag_posts=tag_posts)
    else:
        abort(404)


@app.route('/view')
def view_map():
    """ 文章归档页面路由 """
    if 'adminname' in session:
        is_admin = True
    else:
        is_admin = False
    time_line_posts = get_view_posts_map(Post, is_admin)
    tag_map = get_view_tag_map(Tag)
    return render_template('view_view.html', time_line_posts=time_line_posts, tag_map=tag_map)


@app.route('/message', methods=['GET', 'POST'])
def message():
    '''
    查询留言页面路由
    '''
    if request.method == 'POST':
        the_result = do_message(db, Message, request.form, request.remote_addr)
        return the_result
    else:
        all_messages = Message.query.order_by(Message.post_time.desc()).all()
        return render_template('view_message.html', all_messages=all_messages)


@app.route('/comment', methods=['POST'])
def blog_comment():
    """ 博客文章评论 """
    the_result = do_blog_comment(db, Post, Comment, request.form, request.remote_addr)
    return the_result


@app.route('/check_view_pwd', methods=['POST'])
def check_view():
    """ 验证查看密码 """
    the_result = check_view_pwd(db, Post, Option, request.form)
    return the_result


@app.route('/secret/<view_id>')
def get_secret(view_id):
    """ 查看加密文章 """
    the_post = get_secret_post(db, Post, Option, view_id)  # 获取指定id的加密博文
    if the_post:
        return render_template('view_secret.html', the_post=the_post)
    else:
        abort(404)


@app.route('/about')
def about_me():
    """ 关于我的简介 """
    return render_template('view_about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ 登录管理后台页面路由 """
    session.permanent = True  # 设置关闭浏览器重新打开还保存session
    if request.method == 'POST':
        if 'adminname' in session:
            return redirect(url_for('index'))
        else:
            # 将‘adminname’属性放入session中，在本次request返回response的时候，服务器发送了将
            # session放到 cookies的指令，将session存储到客户端浏览器
            form_adminname = request.form['username']
            form_adminpwd = hashlib.sha256(request.form['password'].encode(encoding='utf-8')).hexdigest()
            db_adminname = Option.query.filter_by(option_name='admin_name').first().option_value
            db_adminpwd = Option.query.filter_by(option_name='admin_pwd').first().option_value
            if form_adminname == db_adminname and form_adminpwd == db_adminpwd:
                session['adminname'] = form_adminname
                return url_for('manage_blog')
            else:
                return 'error'

    else:
        if 'adminname' in session:
            return redirect(url_for('manage_blog'))
        else:
            return render_template('admin_login.html')


@app.route('/logout')
def logout():
    """ 如果会话中有用户名就删除它,同时从客户端浏览器中删除session的adminname属性 """
    session.pop('adminname', None)
    return redirect(url_for('index'))


@app.route('/manage/blog', methods=['GET', 'POST'])
def manage_blog():
    """ 博文管理页面路由 """
    if 'adminname' in session:
        if request.method == 'POST':
            del_result = manage_del_blog(db, Post, Comment, request.form.get('edit_id'))
            return del_result
        else:
            blog_list = Post.query.order_by(Post.post_time.desc()).all()
            return render_template('admin_blog.html',
                                   page_in='blog',
                                   blog_list=blog_list)
    else:
        return redirect(url_for('login'))


@app.route('/manage/edit/<edit_id>', methods=['GET', 'POST'])
def manage_edit(edit_id):
    """ 文章编辑页面路由 """
    if 'adminname' in session:
        if request.method == 'POST':
            if edit_id == 'new':
                the_id = edit_a_blog(db, Post, Tag, request.form)
            else:
                the_id = edit_a_blog(db, Post, Tag, request.form, edit_id)
            if the_id:
                return url_for('get_post', post_id=the_id)
            else:
                abort(404)
        else:
            all_tags = all_tags_list(Tag)
            if edit_id == 'new':
                return render_template('admin_edit.html',
                                       page_in='edit',
                                       tags=all_tags)
            else:
                the_post_query = Post.query.filter_by(edit_id=edit_id).first()
                if the_post_query:
                    return render_template('admin_edit.html',
                                           page_in='edit',
                                           edit_id=edit_id,
                                           tags=all_tags,
                                           post_query=the_post_query)
                else:
                    abort(404)
    else:
        return redirect(url_for('login'))


@app.route('/manage/draft', methods=['GET', 'POST'])
def manage_draft():
    """ 草稿列表页面路由 """
    if 'adminname' in session:
        if request.method == 'POST':
            del_result = manage_del_blog(db, Post, Comment, request.form.get('edit_id'))
            return del_result
        else:
            draft_list = Post.query.filter(Post.post_status == 'draft').order_by(Post.post_time.desc()).all()
            return render_template('admin_draft.html',
                                   page_in='draft',
                                   blog_list=draft_list)
    else:
        return redirect(url_for('login'))


@app.route('/manage/tag', methods=['GET', 'POST'])
def manage_tag():
    """ 标签列表页面路由 """
    if 'adminname' in session:
        if request.method == 'POST':
            the_result = manage_the_tag(db, Tag, request.form)
            return the_result
        else:
            all_tags = Tag.query.all()
            return render_template('admin_tag.html',
                                   page_in='tag',
                                   all_tags=all_tags)
    else:
        return redirect(url_for('login'))


@app.route('/manage/comment', methods=['GET', 'POST'])
def manage_comment():
    """ 评论列表页面路由 """
    if 'adminname' in session:
        if request.method == 'POST':
            the_result = manage_the_comment(db, Comment, request.form)
            return the_result
        else:
            all_comments = Comment.query.order_by(Comment.post_time.desc()).all()
            return render_template('admin_comment.html',
                                   page_in='comment',
                                   all_comments=all_comments)
    else:
        return redirect(url_for('login'))


@app.route('/manage/message', methods=['GET', 'POST'])
def manage_message():
    """ 留言列表页面路由 """
    if 'adminname' in session:
        if request.method == 'POST':
            the_result = manage_the_message(db, Message, request.form)
            return the_result
        else:
            all_messages = Message.query.order_by(Message.post_time.desc()).all()
            return render_template('admin_message.html',
                                   page_in='message',
                                   all_messages=all_messages)
    else:
        return redirect(url_for('login'))


@app.route('/manage/admin', methods=['POST'])
def manage_admin():
    """ 管理员资料页面路由 """
    if 'adminname' in session:
        the_result = manage_the_admin(db, Option, request.form)
        return the_result
    else:
        abort(404)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    """ 图片上传路由 """
    if 'adminname' in session:
        if request.files.get('image_file'):
            link_url = save_image(db, File, request.files.get('image_file'))
            return jsonify({"link": link_url})
        else:
            abort(404)
    else:
        abort(404)


@app.route('/load_images')
def load_images():
    """ 图片列表加载 """
    if 'adminname' in session:
        all_images = load_all_images(File)
        return jsonify(all_images)
    else:
        abort(404)


@app.route('/delete_image', methods=['POST'])
def delete_image():
    """ 删除已上传图片 """
    if 'adminname' in session:
        del_the_image(db, File, request.form)
        return jsonify('ok')
    else:
        abort(404)


@app.route('/upload_video', methods=['POST'])
def upload_video():
    """ 视频上传路由 """
    if 'adminname' in session:
        if request.files.get('video_file'):
            link_url = save_video(db, File, request.files.get('video_file'))
            return jsonify({"link": link_url})
        else:
            abort(404)
    else:
        abort(404)


@app.route('/upload_file', methods=['POST'])
def upload_file():
    """ 文件上传路由 """
    if 'adminname' in session:
        if request.files.get('the_file'):
            link_url = save_file(db, File, request.files.get('the_file'))
            return jsonify({"link": link_url})
        else:
            abort(404)
    else:
        abort(404)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """ 发送静态文件 """
    file_path, the_file = get_the_file(filename)
    return send_from_directory(file_path, the_file)


@app.errorhandler(404)
def page_not_found(e):
    # 404错误页面模板定制
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    # 500错误页面模板定制
    return render_template('500.html'), 500


def md5email(email):
    # 模板中对邮箱地址进行MD5计算
    return hashlib.md5((email.lower()).encode(encoding='utf-8')).hexdigest()


def get_info(option):
    # 模板中输出通用信息
    if option == 'name':  # 管理员昵称
        return (Option.query.filter_by(option_name='admin_nickname').first()).option_value
    elif option == 'email':  # 管理员Email
        return (Option.query.filter_by(option_name='admin_email').first()).option_value
    elif option == 'draft':  # 草稿数目
        return Post.query.filter_by(post_status='draft').count()
    elif option == 'comment':  # 未审阅评论
        return Comment.query.filter_by(comment_check=False).count()
    elif option == 'message':  # 未审阅留言
        return Message.query.filter_by(message_check=False).count()


app.add_template_global(md5email, 'md5email')  # 添加模板函数
app.add_template_global(get_info, 'get_info')  # 添加模板函数

if __name__ == '__main__':
    app.run()
