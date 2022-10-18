# -*-coding:utf-8 -*-

"""
# File       : part_by_lines
# Time       ：2022/9/27 14:48
# Author     ：Liu Yuming
# version    ：python 3.9
# Description：
"""

import os, sys

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(FILE_DIR, '../utils'))
import argparse
import random

from text import read_lines, write_lines
from base_py_func import str_arg_to_bool, list_sub


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '--src_file',
        type=str,
        help='source file'
    )
    parser.add_argument(
        '--dst_file1',
        type=str,
        help='part1 of dst file'
    )
    parser.add_argument(
        '--dst_file2',
        type=str,
        help='part2 of dst file'
    )
    parser.add_argument(
        '--part1_ratio',
        type=float,
        help='part ratio'
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    # read source file
    src_lines = read_lines(args.src_file)
    print(f'count of source lines: {len(src_lines)}')

    # part by line
    src_size = len(src_lines)
    part1_size = int(src_size * args.part1_ratio)
    index = [i for i in range(src_size)]
    part1_index = random.sample(index, part1_size)
    part2_index = list(set(index) - set(part1_index))
    print(f'length of part1: {len(part1_index)}, length of part2: {len(part2_index)}')

    # write to new files
    part1_lines = [src_lines[i] for i in part1_index]
    part2_lines = [src_lines[i] for i in part2_index]
    write_lines(args.dst_file1, part1_lines)
    write_lines(args.dst_file2, part2_lines)

    print('Done.')
