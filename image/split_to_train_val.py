import os
import sys
from util_func import *
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_path",
        help="The source label list file or image root dir"
    )
    parser.add_argument(
        "step",
        help="The step of validation"
    )
    parser.add_argument(
        "--move_img", action="store_true", 
        help="Switch of move source image or not only works when in_path is image dir"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    in_path = abs_path(args.in_path)
    in_isdir = False
    if os.path.isdir(in_path):
        in_path = modify_dir(in_path)
        in_isdir = True
    step = int(args.step)
    print "in_path: ", in_path
    print "in_isdir: ", in_isdir
    print "step: ", step
    
    if in_isdir:
        out_path_train = modify_dir(in_path[:-1] + ".train")
        out_path_test = modify_dir(in_path[:-1] + ".test")
    else:
        out_path_train = in_path + ".train"
        out_path_test = in_path + ".test"
    print "out_path_train: ", out_path_train
    print "out_path_test: ", out_path_test

    num_train, num_test = 0, 0
    if in_isdir:
        all_imgs = get_imgs(in_path)
        for img_idx, src_img_path in enumerate(all_imgs):
            if img_idx % step == 0:
                num_test += 1
                dst_img_path = replace_root(src_img_path, in_path, out_path_test)
            else:
                num_train += 1
                dst_img_path = replace_root(src_img_path, in_path, out_path_train)
            if args.move_img:
                move_file(src_img_path, dst_img_path)
            else:
                copy_file(src_img_path, dst_img_path)
    else:
        dst_lines_train = []
        dst_lines_test = []
        src_lines = read_lines(in_path)
        for i, line in enumerate(src_lines):
            if i % step == 0:
                dst_lines_test.append(line)
            else:
                dst_lines_train.append(line)
        write_lines(out_path_train, dst_lines_train)
        write_lines(out_path_test, dst_lines_test)
        num_train = len(dst_lines_train)
        num_test = len(dst_lines_test)
    print "num_train: ", num_train
    print "num_test: ", num_test

    print "Done."
