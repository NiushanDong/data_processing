# -*- coding: utf-8 -*-
# Author: Yejinyu (yejinyu@9fbank.com.cn)
# This is a class to pic binarization
import argparse
import json
from multiprocessing import Pool
import numpy as np
import os
import random
import scipy.misc as smp
from util_func import *
import cv2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'pics_path',
        help = "the path of pictures"
    )
    parser.add_argument(
        "text_path",
        help = "the standard label path of pictures"
    )
    parser.add_argument(
        "pic_save_path",
        help = "the path of saving picture"
    )
    parser.add_argument(
        "text_save_path",
        help = "the path of saving standard label"
    )
    parser.add_argument(
        "degree_arange1",
        help = "the left border of rotate degree"
    )
    parser.add_argument(
        "degree_arange2",
        help = "the right border of rotate degree"
    )
    parser.add_argument(
        "rotate_num",
        help = "the number of retation"
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

def rotate(pics_path, text_path, pic_save_path, text_save_path, degree_arange1, degree_arange2, rotate_num):
    picParas = get_para(text_path)
    file_object = open(text_save_path, 'a')

    for picPara in picParas:
        pic_path = os.path.join(pics_path, picPara[0])
        img = cv2.imread(pic_path)
        mean_Y = np.mean(img, axis = 1)
        mean_Z = np.mean(mean_Y, axis = 0)
        
        for count in range(rotate_num):
            img_copy = img
            row, col, channel = img_copy.shape
            size = int(pow(row * row + col * col, 0.5)) + 20
            translate = np.zeros(2, np.int32)
            add_num = (size - row) / 2
            translate[1] = add_num
            add_x = mean_Z * np.ones((add_num, col, 3), np.int32)

            img_copy = np.vstack((add_x, img_copy))

            img_copy = np.vstack((img_copy, add_x))

            row, col, channel = img_copy.shape
            add_num = (size - col) / 2

            translate[0] = add_num

            add_y = mean_Z * np.ones((row, add_num, 3), np.int32)
            img_copy = np.hstack((add_y, img_copy))

            img_copy = np.hstack((img_copy, add_y))

            translate_points = picPara[1] + translate

            degree = random.randint(degree_arange1, degree_arange2)

            row, col, channel = img_copy.shape
            M = cv2.getRotationMatrix2D((col/2, row/2), degree, 1.0)

            img_copy = smp.toimage(img_copy)
            img_copy = np.array(img_copy)
            dst = cv2.warpAffine(img_copy, M, (row, col))

            points = np.vstack((translate_points.T, np.ones(4)))
            retate_points = np.dot(M, points)
            retate_points = retate_points.T
            retate_points = retate_points.astype(int)
            '''
            for p in retate_points:
                dst = cv2.circle(dst, (p[0], p[1]), 5, (255,0,0), 5)
            '''
            if not os.path.exists(pic_save_path):
                os.mkdir(pic_save_path)
            filename_series = picPara[0].split('.')
            filename = filename_series[0] + '_1_' + str(count) + '.' + filename_series[-1]
            save_file = os.path.join(pic_save_path, filename)
            new_img = smp.toimage(dst)
            new_img = np.array(new_img)
            cv2.imwrite(save_file, new_img)
            location = {"angular_points": {"topleft": [retate_points[0,0],retate_points[0,1]], "bottomleft": [retate_points[1,0],retate_points[1,1]],
                               "topright": [retate_points[2,0],retate_points[2,1]], "bottomright": [retate_points[3,0],retate_points[3,1]]},
                               "size": [row, col]}
            location_json = json.dumps(location)
            file_object.write('%s\t%s\n' %(filename, location_json))
            print filename        
    file_object.close()

if __name__ == '__main__':
    args = parse_args()
    pics_path = abs_path(args.pics_path)
    text_path = abs_path(args.text_path)
    pic_save_path = abs_path(args.pic_save_path)
    text_save_path = abs_path(args.text_save_path)
    degree_arange1 = float(args.degree_arange1)
    degree_arange2 = float(args.degree_arange2)
    rotate_num = int(args.rotate_num)
    
    rotate(pics_path, text_path, pic_save_path, text_save_path, degree_arange1, degree_arange2, rotate_num)
    

