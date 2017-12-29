# -*- coding: utf-8 -*-
# Author: Yejinyu (yejinyu@9fbank.com.cn)
# This is a class to rename the picture by hash

from PIL import Image
import imagehash
import os
import argparse

def run(filePara):
    file_extension = ['.jpg', '.png']
    if isinstance(filePara, str) and os.path.exists(filePara):
        for file in os.listdir(filePara):
            if file[-4:] in file_extension:
                des_path = os.path.join(filePara, file)
                hash1 = str(imagehash.average_hash(Image.open(des_path)))
                hash2 = str(imagehash.phash(Image.open(des_path)))
                hashName = hash1 + '_' + hash2 + file[-4:]
                os.rename(des_path, os.path.join(filePara, hashName))
                return

    elif isinstance(filePara, list):
        for filePath in filePara:
            if os.path.exists(filePath):
                hash1 = str(imagehash.average_hash(Image.open(filePath)))
                hash2 = str(imagehash.phash(Image.open(filePath)))
                hashName = hash1 + '_' + hash2 + filePath[-4:]
                seg = filePath.split('/')
                seg[-1] = hashName
                newName = '/'.join(seg)
                os.rename(filePath, newName)
                return
            else:
                print 'the file %s is not exist' %filePath

    else:
        print 'input error'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path",
        help="The root dir of images."
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    input_path = args.input_path
    run(input_path)
    print "Done."
