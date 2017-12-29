from util_func import *
import time
import argparse
import math
import json
import random
from multiprocessing import Pool
import cv2
import numpy as np
import lmdb
import h5py
import shutil

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "label_file",
        help = "The angular pos label file."
    )
    parser.add_argument(
        "image_root",
        help = "The root dir of images."
    )
    parser.add_argument(
        "mask_root",
        help = "The root dir of mask images."
    )
    parser.add_argument(
        "pos_db_root",
        help = "The dir of angular position hdf5 file."
    )
    parser.add_argument(
        "--image_db",
        default="",
        help = "The lmdb dir of image and mask."
    )
    parser.add_argument(
        "--mask_db",
        help = "The lmdb dir of mask images.", 
        default = ""
    )
    parser.add_argument(
        "--hdf5_with_img",
        help = "The switch of write image data to hdf5 or not.", 
        default = 0
    )
    parser.add_argument(
        "--resize_w",
        help = "The resized width of image and mask",
        default = 256
    )
    parser.add_argument(
        "--resize_h",
        help = "The resized height of image and mask",
        default = 256
    )
    parser.add_argument(
        "--lmdb_tool",
        help = "The caffe lmdb tool",
        default = "/app/dev_user/projects/caffe-master/build/tools/convert_imageset"
    )

    return parser.parse_args()

def parse_pos_label(label):
    points = []
    w = label["size"][0]
    h = label["size"][1]
    points += label["angular_points"]["topleft"]
    points += label["angular_points"]["topright"]
    points += label["angular_points"]["bottomleft"]
    points += label["angular_points"]["bottomright"]

    for i in range(len(points)):
        if i % 2 == 0:
            points[i] /= float(w)
        else:
            points[i] /= float(h)
        if points[i] > 1.0:
            points[i] = 1.0
        if points[i] < 0.0:
            points[i] = 0.0

    return points

def write_lmdb(all_imgs, all_labels):
    global image_root, mask_root, image_db, mask_db, lmdb_tool, resize_w, resize_h

    # write image data to lmdb file
    if not image_db == "":
        list_file = "tmp.txt"
        dst_lines = []
        for one in all_imgs:
            sub_path = one[len(image_root):]
            dst_lines.append(sub_path)
        write_lines(list_file, dst_lines)
        cmd = "{} --resize_height={} --resize_width={} --backend={} {} {} {}".format(
                lmdb_tool, resize_h, resize_w, "lmdb", image_root, list_file, image_db)
        print "Creating image lmdb..."
        os.system(cmd)

    # write mask data to lmdb file
    if not mask_db == "":
        dst_lines = []
        for img_path in all_imgs:
            mask_path = all_labels[img_path]["mask"]
            dst_lines.append(mask_path[len(mask_root):])
        write_lines(list_file, dst_lines)
        cmd = "{} --backend={} --gray {} {} {}".format(
                lmdb_tool, "lmdb", mask_root, list_file, mask_db)
        print "Creating mask lmdb..."
        os.system(cmd)

    try_remove(list_file)

def preprocess(img_path):
    global resize_w, resize_h
    mean = [104, 117, 123]
    mean = np.asarray(mean, dtype=np.float32)
    mean = mean[:, np.newaxis, np.newaxis]
    scale = 0.003921568627451
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (resize_w, resize_h))
    img = img.astype(np.float32)
    img = img.transpose([2,0,1])
    img -= mean
    img *= scale
    return img

def write_hdf5(all_imgs, all_labels):
    global pos_db_root, hdf5_with_img, resize_w, resize_h
    
    all_parts = []
    img_num = len(all_imgs)
    if hdf5_with_img == 1:
        # split to several parts
        step = 2000
        part_num = int(math.ceil(float(img_num) / step))
        for i in range(part_num):
            start = i * step
            end = (i + 1) * step
            end = img_num if end > img_num else end
            all_parts.append(all_imgs[start:end])
    else:
        all_parts.append(all_imgs)

    all_dbs = []
    all_num = 0
    for part_idx, one_part in enumerate(all_parts):
        db_path = os.path.join(pos_db_root, "{}.hdf5".format(part_idx))
        h5_strm = h5py.File(db_path, "w")
        
        # write angular position
        data_len = 8
        pos_data = np.zeros((len(one_part), data_len), dtype=np.float32)
        for i, img_path in enumerate(one_part):
            data = np.asarray(all_labels[img_path]["pos"], dtype=np.float32)
            pos_data[i] = data
        h5_strm.create_dataset('label', data=pos_data)
        
        # write image data
        if hdf5_with_img == 1:
            data_len = resize_w * resize_h * 3
            imgs = np.zeros((len(one_part), 3, resize_h, resize_w), dtype=np.float32)
            for i, img_path in enumerate(one_part):
                imgs[i] = preprocess(img_path)
            h5_strm.create_dataset("data", data=imgs)
        h5_strm.close()

        all_dbs.append(db_path)
        print "%d boxes to hdf5" % pos_data.shape[0]
        all_num += pos_data.shape[0]
    print "Totally %d boxes to hdf5" % all_num
    
    list_file = pos_db_root + ".list"
    write_lines(list_file, all_dbs)

def process():
    global label_file, image_root, mask_root, hdf5_with_img
    
    # read label file
    all_labels = {}
    lines = read_lines(label_file)
    for line in lines:
        pos = line.find("\t")
        if pos == -1:
            continue
        img_path = line[:pos]
        img_path = os.path.join(image_root, img_path)
        if not os.path.exists(img_path):
            print "warning: %s not exist and will be skipped!" % img_path
            continue
        mask_path = img_path.replace(image_root, mask_root)

        if not os.path.exists(mask_path):
            print "warning: mask of %s not exist and will be skipped!" % mask_path
            continue

        pos = parse_pos_label(json.loads(line[pos+1:]))

        all_labels[img_path] = {"pos":pos, "mask":mask_path}
    print "len of all_labels: ", len(all_labels.keys())

    # shuffle image list
    all_imgs = all_labels.keys()
    random.shuffle(all_imgs)

    # write db
    write_hdf5(all_imgs, all_labels)
    write_lmdb(all_imgs, all_labels)

if __name__ == "__main__":
    args = parse_args()
    label_file = abs_path(args.label_file)
    image_root = abs_path(args.image_root)
    mask_root = abs_path(args.mask_root)
    image_db = abs_path(args.image_db)
    mask_db = abs_path(args.mask_db)
    pos_db_root = abs_path(args.pos_db_root)
    resize_w = int(args.resize_w)
    resize_h = int(args.resize_h)
    lmdb_tool = abs_path(args.lmdb_tool)
    hdf5_with_img = int(args.hdf5_with_img)
 
    if hdf5_with_img == 1:
        print "hdf5 with image data"
    else:
        print "hdf5 without image data"

    if not image_root.endswith("/"):
        image_root += "/"
    if not mask_root.endswith("/"):
        mask_root += "/"
    
    if os.path.exists(image_db):
        print "{} already exist, remove it and try again!".format(image_db)
        sys.exit(1)
    if os.path.exists(mask_db):
        print "{} already exist, remove it and try again!".format(mask_db)
        sys.exit(1)
    if os.path.exists(pos_db_root):
        print "{} already exist, remove it and try again!".format(pos_db_root)
        sys.exit(1)
    try_make_dir(pos_db_root)

    time_s = time.time()
    random.seed(time_s)
    process()
    time_e = time.time()
    print "Totally takes %f min" % ((time_e - time_s) / 60);

    print "Done."


