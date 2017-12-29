# -*- coding: utf-8 -*-
import utils
import cv2
import os
import numpy as np
import time
import random
from render_font import render_font
from distortion import distort_image
from back_blend import back_blend
from blur_noise import image_blur, image_noise
from multiprocessing import Pool
from PIL import Image


def img_resize(img, new_h, fixed_len):
    h, w = img.shape[:2]
    new_w = 10 * new_h if fixed_len \ 
            else max(min(30 * new_h, int(new_h * w / h)), new_h)
    img = cv2.resize(np.array(img), (new_w, new_h))
    return img, new_w


def gen_one_image(word_list, fixed_len, file_list, color_centers):
    '''根据word_list生成一张图'''
    # 字体绘制
    img = render_font(word_list, size=64, gap=1.0, resize_factor=1.0)
    # 畸变
    img = distort_image(img, angle=2.0, r=0.05, factor=0.8)
    h, w = np.array(img).shape[:2]
    img = cv2.resize(np.array(img), (int(64 * w / h), 64))
    img = image_noise(img, var=0.005)
    img = image_blur(img, size=3)
    # 背景混合，出来是RGBA
    img = back_blend(
            img=np.array(img), file_list=file_list, 
            color_centers=color_centers)
    #img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    rd_h = 32
    img, new_w = img_resize(img, rd_h, fixed_len)

    return img, new_w


def gen_train(dst_dir, vocab_file, file_list, color_centers):
    '''生成训练数据'''
    process_id = os.getpid()
    print('process %d begin ...' % process_id)

    vocab_list = utils.get_vocab_list(vocab_file)
    vocab_size = len(vocab_list)

    print('vocab_size %d' % vocab_size)
    img_count = 0
    for idx_batch in range(100):
        for idx_len in range(20, 21):
            length_scale = idx_len
            current_vocab_list = vocab_list * length_scale
            random.shuffle(current_vocab_list)
            idx_img = 0
            # while idx_img < vocab_size:
            while idx_img < length_scale * vocab_size:
                # 生成文字图
                word_list = current_vocab_list[idx_img: idx_img + idx_len]
                # 不单独生成'-'的样本
                if len(word_list) == 1 and word_list[0] == '-':
                    idx_img += idx_len
                    continue
                img, img_w = gen_one_image(
                        word_list=word_list, 
                        fixed_len=False,
                        file_list=file_list,
                        color_centers=color_centers)

                # 写文件
                quality = min(100, max(40, int(100 * (0.7 + 0.3 * np.random.randn()))))
                word_string = ''.join(word_list)
                img_name = str(process_id) + '_' + str(idx_batch) + '_' + \
                        str(idx_len) + '_' + str(idx_img) + \
                        '_' + str(quality) + '_' + str(img_w) + \
                        '_' + word_string + '.jpg'
                img_name = os.path.join(dst_dir, img_name)
                img = Image.fromarray(img)
                img.save(
                        img_name, format='JPEG', quality=quality,
                        optimize=True, progressive=True)

                idx_img += idx_len
                img_count += 1
                print('%s ---- %d' % (img_name, img_count))


bg_dir = '../0000/9130bg'
file_list = os.listdir(bg_dir)
file_list = [os.path.join(bg_dir, f) for f in file_list]
dst_dir = '../0000/26long'
vocab_file = './26_ctc.txt'
color_centers = np.load('all_lab_colors.npy')

if not os.path.exists(dst_dir):
    os.mkdir(dst_dir)


if __name__ == '__main__':

    start = time.time()
    cpu_count = os.cpu_count()
    print('cpu_count %d' % cpu_count)
    #gen_train(dst_dir, vocab_file, file_list, color_centers)
    p = Pool(cpu_count)
    for i in range(cpu_count):
        p.apply_async(
                gen_train, args=(dst_dir, vocab_file, file_list, color_centers,))
        print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done. Time cost %f' % (time.time() - start))
