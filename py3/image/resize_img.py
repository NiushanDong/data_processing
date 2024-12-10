# -*- coding: utf-8 -*-

import argparse
import os
import sys
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/py3"))
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
    parser.add_argument(
        "--cpu_ratio",
        default=0.8,
        help="number of parallel, default is 0.8*<cpu_num>"
    )
    return parser.parse_args()

def process(arg_zip):
    src_images, args = arg_zip

    # resize and save dst image
    for n, src_path in enumerate(src_images):
        img = cv2.imread(src_path)
        if img is None:
            continue
        img = cv2.resize(
                img, (args.dst_width, args.dst_height),
                interpolation=cv2.INTER_LINEAR)
        dst_path = src_path.replace(args.src_img_root, args.dst_img_root)
        write_img(dst_path, img)

        if (n + 1) % 1000 == 0:
            print(f'{n + 1} of this worker done')

if __name__ == "__main__":
    args = parse_args()
    args.src_img_root = modify_dir(abs_path(args.src_img_root))
    args.dst_img_root = modify_dir(abs_path(args.dst_img_root))
    args.dst_width = int(args.dst_width)
    args.dst_height = int(args.dst_height)
    print("args: ", args)
    
    # get src image path
    src_imgs = get_imgs(args.in_imgs)
    print("Got {} input images".format(len(src_imgs)))

    # resize parallel
    worker_num = auto_proc_num(ratio=args.cpu_ratio)
    print(f'number of worker: {worker_num}')
    all_parts = list_group(src_imgs, worker_num)
    all_parts = [(one, args) for one in all_parts]
    pool = Pool(worker_num)
    pool.map(process, all_parts)
    
    print("Done.")
