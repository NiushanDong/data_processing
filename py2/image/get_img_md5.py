import os
import sys
import commands
import shutil
from multiprocessing import Pool
import argparse
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/python"))
from util import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_imgs",
        help="The image root dir or image list file."
    )
    parser.add_argument(
        "md5_file",
        help="The output image md5 file."
    )
    return parser.parse_args()

def img_md5(img_list):
    ret = []
    for i, img_path in enumerate(img_list):
        md5 = commands.getstatusoutput('md5sum ' + img_path)[1].split(" ")[0]
        ret.append((img_path, md5))
        if i % 1000 == 0:
            print "Have Got md5 of %d images" % (i+1)
    return ret

if __name__ == "__main__":
    args = parse_args()
    in_imgs = args.in_imgs
    md5_file = args.md5_file

    all_img_paths = get_imgs(in_imgs)
    
    proc_num = 12
    all_parts = []
    for i in range(proc_num):
        all_parts.append([])
    for i, img_path in enumerate(all_img_paths):
        all_parts[i % proc_num].append(img_path)
    pool = Pool(proc_num)
    all_parts_out = pool.map(img_md5, all_parts)
    all_md5s = []
    for part in all_parts_out:
        all_md5s += part
    
    # write to dst file
    dst_lines = []
    for one in all_md5s:
        dst_lines.append("{} {}".format(one[0], one[1]))
    write_lines(md5_file, dst_lines)
    
    print "Done."
