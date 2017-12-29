#-*- coding:utf-8 -*-

from util_func import *
import json


def get_labels_from_file(label_file):
    lines = read_lines(label_file)
    ret = {}
    for line in lines:
        contents, parter = split_line(line, parter="\t")
        img_path = contents[0]
        label = json.loads(contents[1])
        ret[img_path] = label
    return ret



