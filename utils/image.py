# -*-coding:utf-8 -*-

"""
# File       : image.py
# Time       ：2022/9/27 12:10
# Author     ：Liu Yuming
# version    ：python 3.9
# Description：
"""

import os, sys
import urllib2
from multiprocessing import Pool

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
import argparse
from file_manage import try_make_dir, get_all_files, abs_path
from text import read_lines, split_line


def download_imgs(pairs):
    for i, pair in enumerate(pairs):
        if i % 1000 == 0:
            print("downloaded %d images" % (i+1))
        try:
            url = pair[0]
            print("url: ", url)
            dst_path = pair[1]
            dst_dir = os.path.dirname(dst_path)
            try_make_dir(dst_dir)
            img_content = urllib2.urlopen(url, timeout=2).read()
            with open(dst_path, "w") as strm:
                strm.write(img_content)
        except Exception as err:
            print(err)


def download_imgs_parallel(pairs, proc_num):
    all_parts = []
    for i in range(proc_num):
        all_parts.append([])
    for i, one in enumerate(pairs):
        all_parts[i%proc_num].append(one)
    pool = Pool(proc_num)
    pool.map(download_imgs, all_parts)


def get_imgs_in_folder(folder,
                       backends=[".jpg", ".JPG", ".png", ".PNG", ".bmp", ".BMP"]):
    ret = get_all_files(folder, backends)
    return ret


def get_imgs(path, img_root=None):
    imgs = []
    if os.path.isdir(path):
        imgs = get_imgs_in_folder(path)
    else:
        lines = read_lines(path)
        for line in lines:
            contents, parter = split_line(line)
            img_path = os.path.join(img_root, contents[0]) \
                if not img_root is None else contents[0]
            imgs.append(contents[0])
    for i, one in enumerate(imgs):
        imgs[i] = abs_path(one)
    print(imgs)
    return imgs


def append_str_to_imgname(img_path, prefix=None, postfix=None):
    if not prefix is None:
        img_path = prefix + img_path
    if not postfix is None:
        pos = img_path.rfind(".")
        if pos == -1:
            img_path += postfix
        else:
            img_path = img_path[:pos] + postfix + img_path[pos:]
    return img_path


def decode_gif(all):
    for one in all:
        gif_file = one[0]
        img_dir = one[1]
        max_frames = one[2]
        try_make_dir(img_dir)
        os.system("./gif2images {} {} {}".format(gif_file, img_dir, max_frames))

