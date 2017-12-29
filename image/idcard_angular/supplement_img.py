# -*- coding: utf-8 -*-
import argparse
import json
from multiprocessing import Pool
import numpy as np
import os
import random
from util_func import *
from opencv_wrapper import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'src_imgs',
        help = "The root dir or image list file of src images."
    )
    parser.add_argument(
        "src_label_file",
        help = "The label file of src images"
    )
    parser.add_argument(
        'src_img_root',
        help = "The root dir of src images."
    )
    parser.add_argument(
        'dst_img_root',
        help = "The root dir of dst images."
    )
    parser.add_argument(
        "dst_label_file",
        help = "The label file of dst images"
    )
    parser.add_argument(
        "lower_ratio",
        help = "The lower ratio of width or height"
    )
    parser.add_argument(
        "upper_ratio",
        help = "The upper ratio of width or height"
    )
    parser.add_argument(
        "supplement_times",
        help = "The supplement times of each image"
    )
    parser.add_argument(
        "proc_num",
        help = "The process number"
    )

    return parser.parse_args()

def supplement_imgs(src_img_paths):
    global all_labels, src_img_root, dst_img_root, lower_ratio, upper_ratio, \
            supplement_times
    
    new_label_lines = []
    for img_idx, src_img_path in enumerate(src_img_paths):
        img_subpath = src_img_path[len(src_img_root):]
        img_label = all_labels[img_subpath]
        size = img_label["size"]
        src_points = [img_label["angular_points"]["topleft"], 
                img_label["angular_points"]["topright"], 
                img_label["angular_points"]["bottomleft"], 
                img_label["angular_points"]["bottomright"]]
        src_img = cv2.imread(src_img_path)
        w = src_img.shape[1]
        h = src_img.shape[0]

        for i in range(supplement_times):
            ratio_left = random.random() * (upper_ratio - lower_ratio) + lower_ratio
            ratio_right = random.random() * (upper_ratio - lower_ratio) + lower_ratio
            ratio_top = random.random() * (upper_ratio - lower_ratio) + lower_ratio
            ratio_bottom = random.random() * (upper_ratio - lower_ratio) + lower_ratio
            add_sizes = [int(ratio_left * w), int(ratio_right * w), 
                    int(ratio_top * h), int(ratio_bottom * h)]

            dst_img, dst_points = supplement_img(src_img, add_sizes, 
                    src_points=src_points)
            pos = src_img_path.rfind(".")
            dst_img_path = src_img_path[:pos] + "_supplement" + \
                    str(i) + src_img_path[pos:]
            dst_img_path = replace_root(dst_img_path, src_img_root, dst_img_root)
            write_img(dst_img_path, dst_img)

            img_subpath = dst_img_path[len(dst_img_root):]
            dst_label = {"angular_points": {
                    "topleft": dst_points[0], 
                    "topright": dst_points[1], 
                    "bottomleft": dst_points[2], 
                    "bottomright": dst_points[3]}, 
                    "size": size}
            new_label_lines.append("{}\t{}".format(img_subpath, json.dumps(dst_label)))
        
        if (img_idx + 1) % 1000 == 0:
            print "Processed %d" % (img_idx + 1)

    return new_label_lines

def read_labels(label_file):
    ret = {}
    lines = read_lines(label_file)
    for line in lines:
        contents, parter = split_line(line, parter="\t")
        ret[contents[0]] = json.loads(contents[1])
    return ret

if __name__ == '__main__':
    args = parse_args()
    src_imgs = abs_path(args.src_imgs)
    src_label_file = abs_path(args.src_label_file)
    src_img_root = modify_dir(abs_path(args.src_img_root))
    dst_img_root = modify_dir(abs_path(args.dst_img_root))
    dst_label_file = abs_path(args.dst_label_file)
    lower_ratio = float(args.lower_ratio)
    upper_ratio = float(args.upper_ratio)
    supplement_times = int(args.supplement_times)
    proc_num = int(args.proc_num)
    
    random.seed(time.time())
    if lower_ratio < 0.0:
        print "Invalid lower_ratio which should between 0.0 and 1.0"
        sys.exit()
    if upper_ratio < 0.0:
        print "Invalid upper_ratio which should between 0.0 and 1.0"
        sys.exit()

    time_s = time.time()

    # get all images and labels
    all_imgs = get_imgs(src_imgs)
    all_labels = read_labels(src_label_file)

    # part to multi parts
    all_parts = []
    for i in range(proc_num):
        all_parts.append([])
    for i, img_path in enumerate(all_imgs):
        all_parts[i % proc_num].append(img_path)

    # process
    #dst_lines = supplement_imgs(all_imgs)
    pool = Pool(proc_num)
    outputs = pool.map(supplement_imgs, all_parts)
    dst_lines = []
    for one in outputs:
        dst_lines += one
    write_lines(dst_label_file, dst_lines)
    print "Got %d src images" % len(all_imgs)
    print "Created %d dst images" % len(dst_lines)

    time_e = time.time()
    print "Totally takes {} min".format((time_e - time_s)/60)

    print "Done."
