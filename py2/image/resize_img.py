# -*- coding: utf-8 -*-

import argparse
import os
import sys
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/python"))
from util import *
from opencv_wrapper import *


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_imgs", 
        help="source image root or image path list file"
    )
    parser.add_argument(
        "src_img_root", 
        help="src image root dir"
    )
    parser.add_argument(
        "dst_img_root", 
        help="dst image root dir"
    )
    parser.add_argument(
        "dst_width", 
        help="dst image image"
    )
    parser.add_argument(
        "dst_height", 
        help="dst image height"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.src_img_root = modify_dir(abs_path(args.src_img_root))
    args.dst_img_root = modify_dir(abs_path(args.dst_img_root))
    args.dst_width = int(args.dst_width)
    args.dst_height = int(args.dst_height)
    print "args: ", args
    
    # get src image path
    all_src_paths = get_imgs(args.in_imgs)
    print "Got {} input images".format(len(all_src_paths))

    # resize and save dst image
    for src_path in all_src_paths:
        img = cv2.imread(src_path)
        if img is None:
            continue
        img = cv2.resize(
                img, (args.dst_width, args.dst_height), 
                interpolation=cv2.INTER_LINEAR)
        dst_path = src_path.replace(args.src_img_root, args.dst_img_root)
        write_img(dst_path, img)

    print "Done."
