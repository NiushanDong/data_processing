import sys
import os
import argparse
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/python"))
from util import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "img_root",
        help="The root dir of images."
    )
    parser.add_argument(
        "img_list_file",
        help="The output image list."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    img_root = args.img_root
    dst_file = args.img_list_file
    
    allBackends = [".bmp", ".BMP", ".jpeg", ".JPEG", ".jpg", ".JPG", ".png", ".PNG"]
    
    imgNum = 0
    with open(dst_file, "w") as dstStrm:
        for root, dir, files in os.walk(img_root, followlinks=True):
            for imgName in files:
                pos = imgName.rfind(".")
                backend = imgName[pos:]
                if not backend in allBackends:
                    continue
                imgUrl = os.path.join(root, imgName)
                imgUrl = os.path.abspath(imgUrl)
                dstStrm.write(imgUrl+"\n")
        
                imgNum += 1
    
    print "imgNum: ", imgNum
    print "Done."
