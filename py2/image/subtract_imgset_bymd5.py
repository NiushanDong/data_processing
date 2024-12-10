import os
import sys
import shutil
import argparse
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/python"))
from util import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "to_subtract",
        help="The md5 list file of image to subtract."
    )
    parser.add_argument(
        "be_subtracted",
        help="The md5 list file of images to be subtracted."
    )
    return parser.parse_args()

def get_md5_from_file(file_path):
    ret = {}
    lines = read_lines(file_path)
    for line in lines:
        contents, parter = split_line(line)
        ret[contents[0]] = contents[1]
    return ret, parter

if __name__ == "__main__":
    args = parse_args()
    be_subtracted = args.be_subtracted
    subtract = args.to_subtract

    all_to_subtract, parter = get_md5_from_file(args.to_subtract)
    all_be_subtracted, parter = get_md5_from_file(args.be_subtracted)
    md5_be_subtracted = []
    for img, md5 in all_be_subtracted.iteritems():
        md5_be_subtracted.append(md5)

    dst_lines = []
    for img, md5 in all_to_subtract.iteritems():
        if md5 in md5_be_subtracted:
            continue
        dst_lines.append(img + parter + md5)
    write_lines(args.to_subtract, dst_lines)

    print "src num: ", len(all_to_subtract)
    print "num of may be subtracted: ", len(all_be_subtracted)
    print "dst num: ", len(dst_lines)

    print "Done."
