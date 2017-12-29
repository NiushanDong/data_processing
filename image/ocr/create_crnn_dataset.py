# coding=utf-8

import os
import lmdb # install lmdb by "pip install lmdb"
import cv2
import numpy as np
import json
from util_func import *
from opencv_wrapper import *
import pdb

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_imgs",
        help="The root dir of images or image list file."
    )
    parser.add_argument(
        "label_file",
        help="The label file path."
    )
    parser.add_argument(
        "src_img_root",
        help="The root dir of src images."
    )
    parser.add_argument(
        "text_img_root",  
        help="the root dir of cropped text image root."
    )
    parser.add_argument(
        "dataset_path",  
        help="the path of output lmdb dataset."
    )
    parser.add_argument(
        "--remove_previous", action="store_true",
        help="the path of output lmdb dataset."
    )
    return parser.parse_args()


def image_valid(imageBin):
    if imageBin is None:
        return False
    imageBuf = np.fromstring(imageBin, dtype=np.uint8)
    img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
    imgH, imgW = img.shape[0], img.shape[1]
    if imgH * imgW == 0:
        return False
    return True


def write_cache(env, cache):
    with env.begin(write=True) as txn:
        for k, v in cache.iteritems():
            txn.put(k, v)


def create_dataset(outputPath, imagePathList, labelList, 
        lexiconList=None, checkValid=True):
    """
    Create LMDB dataset for CRNN training.

    ARGS:
        outputPath    : LMDB output path
        imagePathList : list of image path
        labelList     : list of corresponding groundtruth texts
        lexiconList   : (optional) list of lexicon lists
        checkValid    : if true, check the validity of every image
    """
    assert(len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    env = lmdb.open(outputPath, map_size=1099511627776)
    cache = {}
    cnt = 0
    dst_lines = []
    for i in xrange(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        if not os.path.exists(imagePath):
            print('%s does not exist' % imagePath)
            continue
        with open(imagePath, 'r') as f:
            imageBin = f.read()
        if checkValid:
            if not image_valid(imageBin):
                print('%s is not a valid image' % imagePath)
                continue

        imageKey = 'image-%09d' % cnt
        labelKey = 'label-%09d' % cnt
        cache[imageKey] = imageBin
        cache[labelKey] = label
        if lexiconList:
            lexiconKey = 'lexicon-%09d' % cnt
            cache[lexiconKey] = ' '.join(lexiconList[i])
        if (cnt + 1) % 1000 == 0:
            write_cache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt+1, nSamples))
        cnt += 1

        dst_lines.append("{}\t{}".format(imagePath, imageKey))

    nSamples = cnt
    cache['num-samples'] = str(nSamples)
    write_cache(env, cache)
    print('Created dataset with %d samples' % nSamples)
    write_lines("image_map.txt", dst_lines)

def get_labels(label_file):
    lines = read_lines(label_file)
    ret = {}
    for line in lines:
        contents, parter = split_line(line, parter="\t")
        img_path = contents[0]
        label = json.loads(contents[1])
        ret[img_path] = label
    return ret


def crop_all_imgs(all_imgs, all_labels):
    global src_img_root, text_img_root
    imgpath_list, label_list = [], []
    for img_idx, img_path in enumerate(all_imgs):
        img_subpath = img_path[len(src_img_root):]
        #print img_subpath
        #pdb.set_trace()
        if not all_labels.has_key(img_subpath):
            #print "Can not find label of {} and skipped".format(img_path)
            continue

        label = all_labels[img_subpath]
        # crop
        src_img = cv2.imread(img_path)
        for roi_idx, one in enumerate(label["text_lines"]):
            lower_x = one["topleft"][0]
            lower_y = one["topleft"][1]
            upper_x = one["bottomright"][0] + 1
            upper_y = one["bottomright"][1] + 1
            text = one["text"].encode("utf-8")
            dst_img = croped_img(src_img, lower_x, upper_x, lower_y, upper_y)
            if dst_img is None:
                continue
            dst_img_path = replace_root(img_path, src_img_root, text_img_root)
            pos = dst_img_path.rfind(".")
            dst_img_path = dst_img_path[:pos] + "_" + str(roi_idx) + dst_img_path[pos:]
            while os.path.exists(dst_img_path):
                pos = dst_img_path.rfind(".")
                dst_img_path = dst_img_path[:pos] + "_" + str(roi_idx) \
                        + dst_img_path[pos:]

            write_img(dst_img_path, dst_img)
            
            imgpath_list.append(dst_img_path)
            label_list.append(text)

    return imgpath_list, label_list

if __name__ == '__main__':
    args = parse_args()
    in_imgs = abs_path(args.in_imgs)
    src_img_root = modify_dir(abs_path(args.src_img_root))
    label_file = abs_path(args.label_file)
    text_img_root = modify_dir(abs_path(args.text_img_root))
    dataset_path = modify_dir(abs_path(args.dataset_path))[:-1]
    remove_previous = args.remove_previous
    print "in_imgs: ", in_imgs
    print "src_img_root: ", src_img_root
    print "label_file: ", label_file
    print "text_img_root: ", text_img_root
    print "dataset_path: ", dataset_path
    print "remove_previous: ", remove_previous

    if remove_previous:
        try_remove(text_img_root)
        try_remove(dataset_path)

    time_s = time.time()

    # get all image path
    all_imgs = get_imgs(in_imgs, src_img_root)
    print "Got %d images from input" % len(all_imgs)

    # get text location and contents label from file
    all_labels = get_labels(label_file)
    print "Got %d labels from label_file" %len(all_labels)

    # save cropped text images
    imgpath_list, label_list = crop_all_imgs(all_imgs, all_labels)
    print "Cropped %d images" % len(imgpath_list)

    # write lmdb
    create_dataset(dataset_path, imgpath_list, label_list)
    
    time_e = time.time()
    print "Totally toke {} min".format((time_e - time_s) / 60)

    print "Done."
