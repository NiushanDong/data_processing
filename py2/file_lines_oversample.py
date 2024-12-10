#coding: utf-8

import os
import sys
import argparse
import shutil
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../utils/python"))
from util import *



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("src_file", 
            help="source file")
    parser.add_argument("dst_file", 
            help="destination file")
    parser.add_argument("multi", type = int,
            help="multiply number")
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_arguments()
    print "args: ", args

    lines = read_lines(args.src_file)
    dst_lines = []
    for i in range(args.multi):
        dst_lines += lines

    write_lines(args.dst_file, dst_lines)
    print "Done."
