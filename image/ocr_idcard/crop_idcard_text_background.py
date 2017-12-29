#-*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import random
import codecs
import ipdb
import cv2
import scipy.misc as smp
from util_func import *
from label_func import *
from multiprocessing import Pool


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "src_img_root",
        help="the image root dir of source image."
    )
    parser.add_argument(
        "bg_img_root",
        help="the non-text image root dir."
    )
    parser.add_argument(
        "label_file",
        help="the text label file."
    )
    return parser.parse_args()


def read_word(word_txt):
    f = codecs.open(word_txt, 'r','utf-8')
    lines = f.readlines()
    print len(lines)
    word_char=''
    for line in lines:
        line = line.strip('\n')
        line = line.replace(' ', '')
        word_char += line
    f.close()
    return word_chars


def text_extract(words_set, item_num, length_limit, text_file_path):
    words_num = len(words_set)
    f = open(text_file_path, 'w')
    for i in range(item_num):
        item_list = []
        item_length = random.randint(0, length_limit)
        item_index = [random.randint(0, words_num) for i in range(item_length)]
        item_words = [words_set[index] for index in item_index]
        word_chars = ''.join(item_words)
        f.write(word_chars + '\n')
    f.close()


def get_location(location_json):
    location = location_json['text_lines']
    num = len(location)
    location_list = []
    for unit in location:
        tl = unit['topleft']
        x0 = tl[0]
        y0 = tl[1]
        br = unit['bottomright']
        width = br[0] - x0
        height = br[1] - y0
        location_list.append([x0, y0, width, height])
    return location_list


def get_blank_zone(im, location_box):
    height, width, _ = im.shape
    location_box = np.array(location_box)
    indx = np.argsort(location_box[:, 1])
    location_box = location_box[indx]
    blank_location = []
    x0 = width * 0.05
    y0 = height * 0.05
    x1 = width * 0.95
    y1 = location_box[0, 1]
    if (y1 - y0) > 20:
        blank_location.append([x0, y0, x1, y1])

    x0 = location_box[0, 0] + location_box[0, 2]
    y0 = y0
    x1 = location_box[3, 0] + location_box[3, 2] + location_box[0, 2] * 0.3
    y1 = location_box[1, 1]
    if (y1 - y0) > 20:
        blank_location.append([x0, y0, x1, y1])
    
    x0 = width * 0.05
    y0 = location_box[-2, 1] + location_box[-2, 3]
    x1 = location_box[3, 0] + location_box[3, 2]
    y1 = location_box[-1, 1]
    if (y1 - y0) > 20:
        blank_location.append([x0, y0, x1, y1])
    
    x0 = width * 0.05
    y0 = location_box[-1, 1] + location_box[-1, 3]
    x1 = width * 0.95
    y1 = height * 0.95
    if (y1 - y0) > 20:
        blank_location.append([x0, y0, x1, y1])

    blank_location = np.array(blank_location)
    blank_location = blank_location.astype(int)
    return blank_location


def generate_seg_pics(pic_path, location_json, pics_save_root):
    im = cv2.imread(pic_path)
    pic_name = pic_path.split('/')[-1]
    height, width, _ =im.shape
    location_box = get_location(location_json)
    dst_zone = get_blank_zone(im, location_box)
    if dst_zone.shape[0] == 0:
        return 
    for count, box in enumerate(dst_zone):
        im_set = im[box[1]:(box[3]+1), box[0]:(box[2]+1)]
        im_subset = im_set.copy()
        try:
            new_img = smp.toimage(im_subset)
        except Exception as err:
            print err
            return 
        new_img = np.array(new_img)
        pic_save_path = os.path.join(
                pics_save_root, "{}_{}_{}".format(i, count, pic_name))

        cv2.imwrite(pic_save_path, new_img)


def crop_bgimg_multi(inputs):
    for one in inputs:
        generate_seg_pics(one[0], one[1], one[2])

if __name__ == '__main__':
    args = parse_args()
    args.src_img_root = modify_dir(abs_path(args.src_img_root))
    args.bg_img_root = modify_dir(abs_path(args.bg_img_root))
    print "args: ", args

    try_make_dir(args.bg_img_root)

    all_labels = get_labels_from_file(args.label_file)
    print "Got labels of {} images".format(len(all_labels.keys()))

    print 'Start...'
    proc_num = 12
    all_parts = []
    for i in range(proc_num):
        all_parts.append([])

    for i, key in enumerate(all_labels.keys()):
        pic_path = os.path.join(args.src_img_root, key)
        all_parts[i % proc_num].append([pic_path, all_labels[key], args.bg_img_root])

    for i in range(proc_num):
        crop_bgimg_multi(all_parts[i])

    #pool = Pool(proc_num)
    #pool.map(crop_bgimg_multi, all_parts)
    #pool.close()
    #pool.join()
    
    print 'Done...'
    


         
