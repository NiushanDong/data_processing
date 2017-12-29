# -*- coding: utf-8 -*-

import sys
from opencv_wrapper import *
from util_func import *
import lmdb
import argparse
import ipdb


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "lmdb_path", 
            help="path of lmdb dataset")
    parser.add_argument(
            "key_file", 
            help="the path of keys file, one per line")
    parser.add_argument(
            "dst_img_root", 
            help="the root path dst image")
    parser.add_argument(
            "dst_label_file", 
            help="the path dst label file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.lmdb_path = abs_path(args.lmdb_path)
    args.key_file = abs_path(args.key_file)
    args.dst_img_root = modify_dir(abs_path(args.dst_img_root))
    print "args: ", args

    try_make_dir(args.dst_img_root)
    try_make_dir(os.path.dirname(args.dst_label_file))

    # get all keys from file
    lines = read_lines(args.key_file)
    img_keys = []
    label_keys = []
    for line in lines:
        contents, parter = split_line(line, parter=",")
        flag, key = contents[0], contents[1]
        if flag == "image":
            img_keys.append(key)
        elif flag == "label":
            label_keys.append(key)

    # read lmdb and save
    env = lmdb.open(args.lmdb_path)
    with env.begin() as txn:
        # image
        for key in img_keys:
            img_bin = txn.get(key)
            dst_img_path = os.path.join(args.dst_img_root, key+".jpg")
            with open(dst_img_path, "wb") as strm:
                strm.write(img_bin)

        # label
        with open(args.dst_label_file, "w") as strm:
            dst_lines = []
            for key in label_keys:
                dst_lines.append("{}: {}".format(key+".jpg", txn.get(key)))
            write_lines(args.dst_label_file, dst_lines)

    print "Done."
