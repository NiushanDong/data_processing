# -*- coding: utf-8 -*-
# Author: Yejinyu (yejinyu@9fbank.com.cn)
# This is a class to pic binarization
import argparse
import json
import numpy as np
import os
import scipy.misc as smp
from util_func import *
import cv2
from opencv_wrapper import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "label_file",
        help = "the angular position label file"
    )
    parser.add_argument(
        "save_path",
        help = "the path of saving picture"
    )
    parser.add_argument(
        "resize_w",
        help = "the x of the pixel matrix"
    )
    parser.add_argument(
        "resize_h",
        help = "the y of the pixel matrix"
    )
    parser.add_argument(
        '--img_root',
        help = "the path of pictures",
        default = None
    )
    parser.add_argument(
        '--forground_val',
        help = "the forground mask value",
        default = 1
    )
    return parser.parse_args()

def point_assign(points):
    index = np.lexsort(points.T)
    points = points[index]
    if points[0, 0] < points[1, 0]:
        p0 = points[0]
        p1 = points[1]
    else:
        p0 = points[1]
        p1 = points[0]

    if points[2, 0] < points[3, 0]:
        p2 = points[2]
        p3 = points[3]
    else:
        p2 = points[3]
        p3 = points[2]
    return np.array([p0, p1, p2, p3])

def get_para(file):
    with open(file, 'r') as text:
        line = text.readline()
        picParas = []
        while line:
            picPara = []
            points = np.zeros((4,2))
            paras = line.split('\t')
            picPara.append(paras[0])
            pic_json = json.loads(paras[1])
            points_json = pic_json["angular_points"]
            points[0] = np.array(points_json["topleft"])
            points[1] = np.array(points_json["topright"])
            points[2] = np.array(points_json["bottomleft"])
            points[3] = np.array(points_json["bottomright"])
            points = point_assign(points)
            picPara.append(points)
            picParas.append(picPara)
            line = text.readline()
        return picParas

def run(file_path, file, save_path, resize_w, resize_h, forground_val):
    picParas = get_para(file)
    for picPara in picParas:
        if file_path is None:
            pic_path = picPara[0]
            picPara[0] = pic_path.split('/')[-1]
        else:
            pic_path = os.path.join(file_path, picPara[0])
        img = cv2.imread(pic_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (row, col) = gray.shape
        gray = cv2.resize(gray, (resize_w, resize_h), interpolation=cv2.INTER_CUBIC)
        scale_x = resize_w / float(col)
        scale_y = resize_h / float(row)
        points = picPara[1]
        points[:, 0] = points[:, 0] * scale_x
        points[:, 1] = points[:, 1] * scale_y

        points = np.int32(points[[0,1,3,2]])
        new_img = np.zeros((resize_h, resize_w), np.uint8)
        cv2.fillConvexPoly(new_img, points, forground_val)

        save_file = os.path.join(save_path, picPara[0])
        new_img = smp.toimage(new_img)
        new_img = np.array(new_img)
        write_img(save_file, new_img)


if __name__ == '__main__':

    args = parse_args()
    img_root = args.img_root
    label_file = args.label_file
    save_path = args.save_path
    try_make_dir(save_path)
    resize_w = int(args.resize_w)
    resize_h = int(args.resize_h)
    forground_val = int(args.forground_val)

    run(img_root, label_file, save_path, resize_w, resize_h, forground_val)



