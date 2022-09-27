
#-*- coding: utf-8 -*-

# @File Name   : text.py
# @Created Time: 2022-09-27
# @Author      : liuyuming@cloudwalk.com


import os
FILE_DIR = os.path.abspath(os.path.dirname(__file__))

from file_manage import try_make_dir


def split_line(line, parter=None):
    if not parter is None:
        contents = line.split(parter)
        return contents, parter

    if not line.find("\t") == -1:
        contents = line.split("\t")
        parter = "\t"
    elif not line.find(" ") == -1:
        contents = line.split(" ")
        parter = " "
    else:
        contents = [line]
        parter = None
    return contents, parter


def read_lines(file, erase_end=True, erase_strs=None):
    ret = []
    with open(file, "r") as strm:
        line_set = set()
        for line in strm.readlines():
            if erase_end:
                line = erase_enter_end(line)
            if not erase_strs is None:
                for one in erase_strs:
                    line = line.replace(one, "")
            ret.append(line)

    return ret


def write_lines(fpath, lines, add_end=True, create_folder=False, append_line=False):
    # create folder
    if create_folder:
        file_dir = os.path.dirname(fpath)
        try_make_dir(file_dir)

    strm = open(fpath, "w") if not append_line else open(fpath, "a")
    for line in lines:
        line = line+"\n" if add_end else line
        strm.write(line)
    strm.close()


def write_lists(fpath, data_all, parter=","):
    if data_all is None:
        return
    try_make_dir(os.path.dirname(fpath))
    all_lines = []
    for data in data_all:
        if data is None:
            continue
        all_lines.append(parter.join(data))

    write_lines(fpath, all_lines)


def erase_repeat(src_list):
    if src_list is None:
        return None
    data_set = set(src_list)
    ret = []
    for one in data_set:
        ret.append(one)

    return ret


def erase_enter_end(src_str):
    if src_str.endswith("\r\n"):
        src_str = src_str[:-2]
    elif src_str.endswith("\n"):
        src_str = src_str[:-1]

    return src_str


