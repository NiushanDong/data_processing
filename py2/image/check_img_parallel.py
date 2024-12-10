import os
import sys
import cv2
import shutil
from multiprocessing import Pool
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/python"))
from util import *


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_imgs",
        help="The dir or path list file of source images"
    )
    parser.add_argument(
        "src_img_root",
        help="The root dir of source images"
    )
    parser.add_argument(
        "--move_bad", action="store_true", 
        help="The switch of move bad image or not"
    )
    parser.add_argument(
        "--to_color", action="store_true", 
        help="The switch of convert images or not"
    )
    return parser.parse_args()


def check_img(img_list):
    ret = []
    for src_img_path in img_list:
        #if os.path.basename(src_img_path) == "b61aa927-97fa-41c5-8f86-c903fa162184.jpg":
        #    ipdb.set_trace()
        img = cv2.imread(src_img_path, cv2.IMREAD_UNCHANGED)
        # move bad image to other folder
        if img is None \
                or not len(img.shape) == 3 \
                or (not img.shape[2] == 3 and not img.shape[2] == 1):
            dst_img_path = src_img_path.replace(args.src_img_root, args.bad_img_root)
            ret.append((src_img_path, dst_img_path))
            continue

        # convert gray image to color
        if args.to_color and img.shape[2] == 1:
            img = cv2.imread(src_img_path, cv2.IMREAD_COLOR)
            cv2.imwrite(src_img_path, img)
    return ret

if __name__ == "__main__":
    args = parse_args()
    args.src_img_root = modify_dir(abs_path(args.src_img_root))
    args.bad_img_root = args.src_img_root[:-1] + ".bad/"

    # get image list
    all_imgs = get_imgs(args.in_imgs)
    print "number of source images: ", len(all_imgs)

    proc_num = 10
    all_parts = [[] for i in range(proc_num)]
    for i, one in enumerate(all_imgs):
        all_parts[i % proc_num].append(one)
    
    pool = Pool(proc_num)
    outs = pool.map(check_img, all_parts)
    
    # copy or move bad images
    bad_pairs = []
    for one in outs:
        bad_pairs += one
    print "bad image number: ", len(bad_pairs)

    for one in bad_pairs:
        if args.move_bad:
            move_file(one[0], one[1])
        else:
            copy_file(one[0], one[1])

    print "Done."
