
#-*- coding: utf-8 -*-

# @File Name   : file_manage.py
# @Created Time: 2022-09-27
# @Author      : liuyuming@cloudwalk.com


import os
FILE_DIR = os.path.abspath(os.path.dirname(__file__))
import shutil
import pickle


def try_make_dir(path):
    if not os.path.exists(path) and not path == "":
        os.makedirs(path)


def try_make_dir_multi(path_list):
    for path in path_list:
        try_make_dir(path)


def try_remove(path):
    if path == "":
        return
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print("dir: %s removed" % path)
        else:
            os.remove(path)
            print("file: %s removed" % path)


def move_file(src_path, dst_path):
    if not os.path.exists(src_path):
        return
    dst_dir = os.path.dirname(dst_path)
    try_make_dir(dst_dir)
    shutil.move(src_path, dst_path)


def copy_file(src_path, dst_path):
    if not os.path.exists(src_path):
        return
    dst_dir = os.path.dirname(dst_path)
    try_make_dir(dst_dir)
    shutil.copy(src_path, dst_path)


def try_remove_multi(path_list):
    for path in path_list:
        try_remove(path)


def replace_root(src_path, src_root, dst_root):
    if src_path.find(src_root) == -1:
        print("replace_root() ==> src_root not find in src_path")
        return None
    normalize_uri(src_root)
    normalize_uri(dst_root)
    dst_path = src_path.replace(src_root, dst_root)
    return dst_path


def abs_path(path):
    if path == "":
        return ""
    return os.path.abspath(path)


def normalize_uri(uri):
    if uri == "":
        return uri
    if not uri.endswith("/"):
        uri += "/"
    return uri


def get_all_files(root_dir, backends=None):
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if not backends is None:
                for one in backends:
                    if file.endswith(one):
                        file = os.path.join(root, file)
                        all_files.append(file)
            else:
                file = os.path.join(root, file)
                all_files.append(file)
    for i, one in enumerate(all_files):
        all_files[i] = abs_path(one)
    return all_files


def read_pkl(fpath):
    if fpath is None or not os.path.exists(fpath):
        print("{} not exists".format(fpath))
        return None

    with open(fpath, "rb") as strm:
        ret = pickle.load(strm)

    return ret


def write_pkl(fpath, data):
    if fpath is None or data is None:
        return
    try_make_dir(os.path.dirname(fpath))
    with open(fpath, "wb") as strm:
        pickle.dump(data, strm)


