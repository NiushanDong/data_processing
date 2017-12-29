import os
import sys
from util_func import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_file",
        help="The input file."
    )
    parser.add_argument(
        "out_file",
        help="The output file."
    )
    parser.add_argument(
        "cols",
        help="The columns to extract, such as \"0,1\""
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    in_file = args.in_file
    out_file = args.out_file
    cols_to_pick = list(args.cols.split(","))
    cols_to_pick = [int(cols_to_pick[i]) for i in range(len(cols_to_pick))]

    lines = read_lines(in_file)
    print "in %d lines" % len(lines)
    dst_lines = []
    for line in lines:
        contents, parter = split_line(line)
        dst_line = ""
        for i, col_idx in enumerate(cols_to_pick):
            if i == 0:
                dst_line = contents[col_idx]
            else:
                dst_line += parter + contents[col_idx]
        dst_lines.append(dst_line)
    write_lines(out_file, dst_lines)
    print "out %d lines" % len(dst_lines)
    
    print "Done."
