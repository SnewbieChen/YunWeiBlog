# -*- coding: utf-8 -*-
# @Author  : YunWei.Chen
# @Site    : https://chen.yunwei.space

import os
import datetime
from PIL import Image
from config import Config

upload_root_dir = Config.UPLOAD_DIR
base_dir = os.path.dirname(os.path.abspath(__file__))


def save_image(db, File, image_file):
    # 创建文件夹
    image_dir = os.path.join(base_dir, upload_root_dir, datetime.datetime.now().strftime("%Y"),
                             datetime.datetime.now().strftime("%m"), "images")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    base_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    original_filename = base_filename + '_original.' + image_file.filename.split('.')[-1]
    image_file.save(os.path.join(image_dir, original_filename))
    filename = base_filename + '.' + image_file.filename.split('.')[-1]
    with Image.open(image_file) as im:
        im_w, im_h = im.size
        if im_w > 3072 or im_h > 3072:
            im.thumbnail((3072, 3072), resample=Image.LANCZOS)
        im.save(os.path.join(image_dir, filename))
        if im_w > 800 or im_h > 800:
            thumbnail_filename = base_filename + '_thumbnail.' + image_file.filename.split('.')[-1]
            im.thumbnail((800, 800), resample=Image.LANCZOS)
            im.save(os.path.join(image_dir, thumbnail_filename))
        else:
            thumbnail_filename = filename
    link_url = '/' + '/'.join([upload_root_dir, datetime.datetime.now().strftime("%Y"),
                               datetime.datetime.now().strftime("%m"), 'images', filename])
    thumbnail_link_url = '/' + '/'.join([upload_root_dir, datetime.datetime.now().strftime("%Y"),
                                         datetime.datetime.now().strftime("%m"), 'images', thumbnail_filename])
    db_photo = File(name=image_file.filename.split('.')[0:-1],
                    type='photo',
                    upload_time=datetime.datetime.now(),
                    url=link_url,
                    thumbnail_url=thumbnail_link_url)
    db.session.add(db_photo)
    db.session.commit()
    return link_url


def load_all_images(File):
    all_images_query = File.query.filter(File.type == 'photo').order_by(File.upload_time.desc()).all()
    all_images = []
    for n in range(len(all_images_query)):  # 将查询结果转换为Python列表
        all_images.append({
            "url": all_images_query[n].url,
            "thumb": all_images_query[n].thumbnail_url,
            "name": all_images_query[n].name,
            "id": all_images_query[n].id
        })
    return all_images


def del_the_image(db, File, request_form):
    url_path = (request_form.get("src")).split('/')
    image_dir = os.path.join(base_dir, url_path[1], url_path[2], url_path[3], url_path[4])
    image_name, image_type = (url_path[5]).split('.')
    if (url_path[5]).find('thumbnail') > 0:
        original_name = image_name.split('_thumbnail')[0]
        os.remove(os.path.join(image_dir, url_path[5]))  # 删除缩略图
        os.remove(os.path.join(image_dir, original_name + '.' + image_type))  # 删除显示图
        os.remove(os.path.join(image_dir, original_name + '_original.' + image_type))  # 删除原图
    else:
        os.remove(os.path.join(image_dir, url_path[5]))  # 删除缩略图和显示图
        os.remove(os.path.join(image_dir, image_name + '_original.' + image_type))  # 删除原图
    File.query.filter(File.id == request_form.get("id"), File.thumbnail_url == request_form.get("src")).delete()
    db.session.commit()


def save_video(db, File, video_file):
    # 创建文件夹
    video_dir = os.path.join(base_dir, upload_root_dir, datetime.datetime.now().strftime("%Y"),
                             datetime.datetime.now().strftime("%m"), "videos")
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    base_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    filename = base_filename + '.' + video_file.filename.split('.')[-1]
    thumbnail_filename = base_filename + '.jpg'
    video_file.save(os.path.join(video_dir, filename))
    video_path = os.path.join(video_dir, filename)
    thumbnail_path = os.path.join(video_dir, thumbnail_filename)
    os.system('ffmpeg -ss 0.1 -i ' + video_path + ' -f image2 -y ' + thumbnail_path)
    link_url = '/' + '/'.join([upload_root_dir, datetime.datetime.now().strftime("%Y"),
                               datetime.datetime.now().strftime("%m"), 'videos', filename])
    thumbnail_url = '/' + '/'.join([upload_root_dir, datetime.datetime.now().strftime("%Y"),
                                    datetime.datetime.now().strftime("%m"), 'videos', thumbnail_filename])
    db_video = File(name=video_file.filename.split('.')[0:-1],
                    type='video',
                    upload_time=datetime.datetime.now(),
                    url=link_url,
                    thumbnail_url=thumbnail_url)
    db.session.add(db_video)
    db.session.commit()
    return link_url


def save_file(db, File, the_file):
    # 创建文件夹
    file_dir = os.path.join(base_dir, upload_root_dir, datetime.datetime.now().strftime("%Y"),
                            datetime.datetime.now().strftime("%m"), "files")
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    base_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    filename = base_filename + '.' + the_file.filename.split('.')[-1]
    the_file.save(os.path.join(file_dir, filename))
    link_url = '/' + '/'.join([upload_root_dir, datetime.datetime.now().strftime("%Y"),
                               datetime.datetime.now().strftime("%m"), 'files', filename])
    db_file = File(name=the_file.filename.split('.')[0:-1],
                   type='file',
                   upload_time=datetime.datetime.now(),
                   url=link_url)
    db.session.add(db_file)
    db.session.commit()
    return link_url


def get_the_file(filename):
    list_filename = filename.split('/')
    file_path = os.path.join(base_dir, upload_root_dir, *list_filename[:-1])
    return file_path, list_filename[-1]
