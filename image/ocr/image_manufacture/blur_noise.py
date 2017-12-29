# -*- coding: utf-8 -*-
import skimage
import time
import cv2
import random
import numpy as np


def gaussian_blur(img, size):
    kernel_size = random.randint(1, size)
    kernel_size = 2 * kernel_size + 1
    sigma = max(0.2, 1.0 + 1.0 * np.random.randn())
    blur = cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)
    return blur


def motion_blur(img, size):
    '''水平和垂直方向kernel_size可以大点'''
    kernel_id = random.randint(0, 3)
    if kernel_id == 0:  # 水平
        kernel_size = random.randint(1, size - 1)
        kernel = np.zeros((2 * kernel_size + 1, 2 * kernel_size + 1))
        kernel[kernel_size, :] = 1
        kernel = kernel / (2 * kernel_size + 1)
    if kernel_id == 1:  # 反对角
        kernel_size = random.randint(1, size - 2)
        kernel = np.eye(2 * kernel_size + 1)
        kernel = kernel[::-1]
        kernel = kernel / (2 * kernel_size + 1)
    if kernel_id == 2:  # 垂直
        kernel_size = random.randint(1, size - 1)
        kernel = np.zeros((2 * kernel_size + 1, 2 * kernel_size + 1))
        kernel[:, kernel_size] = 1
        kernel = kernel / (2 * kernel_size + 1)
    if kernel_id == 3:  # 对角
        kernel_size = random.randint(1, size - 2)
        kernel = np.eye(2 * kernel_size + 1)
        kernel = kernel / (2 * kernel_size + 1)
    img = cv2.filter2D(img, -1, kernel)
    return img


def image_blur(img, size):
    blur_id = random.randint(0, 2)
    if blur_id == 0:
        blur = gaussian_blur(img, size)
    elif blur_id == 1:
        blur = motion_blur(img, size + 1)
    else:
        return img
    return blur


def image_noise(img, var=0.005):
    mean = 0
    var = random.uniform(0.0, var)
    gauss = skimage.util.random_noise(img, mode='gaussian', mean=mean, var=var)
    gauss = skimage.util.img_as_ubyte(gauss)
    return gauss



