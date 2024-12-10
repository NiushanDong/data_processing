import os
import sys
import argparse
import shutil
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/python"))
from util import *

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("src_root", 
            help="source image root path")
    parser.add_argument("dst_root", 
            help="destination image root path")
    parser.add_argument("pick_step", type = int,
            help="step of picking image")
    parser.add_argument("--move", default=0, type=int,
            help="set as 1 if move file else 0, default is 0")
    args = parser.parse_args()

    return args

def create_dir_if_not_exist(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def cpy_imgs(src_root, dst_root, pick_step):
    if src_root.endswith("/"):
        src_root = src_root[:-1]
    if dst_root.endswith("/"):
        dst_root = dst_root[:-1]
    
    # get all images
    backends = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG"]
    src_num = 0
    dst_num = 0
    for root, dirs, files in os.walk(src_root):
        for file in files:
            pos = file.rfind(".")
            back = file[pos:]
            if not back in backends:
                continue
            src_num += 1
            if src_num % pick_step == 0:
                # make dst folder and copy image
                src_path = os.path.join(root, file)
                dst_path = src_path.replace(src_root, dst_root)
                if args.move == 1:
                    move_file(src_path, dst_path)
                else:
                    copy_file(src_path, dst_path)
                dst_num += 1
    print "src_num: {}".format(src_num)
    print "dst_num: {}".format(dst_num)

def main(args):
    src_root = args.src_root
    dst_root = args.dst_root
    pick_step = args.pick_step
    
    cpy_imgs(src_root, dst_root, pick_step)

if __name__ == "__main__":
    args = parse_arguments()
    print "args: ", args
    main(args)
    print "Done."


