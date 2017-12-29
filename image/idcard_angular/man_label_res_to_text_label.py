# -*- coding: utf-8 -*-

from util_func import *
from opencv_wrapper import *
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'label_root',
        help = "The root dir of label files"
    )
    parser.add_argument(
        'img_root',
        help = "The root dir or image"
    )
    parser.add_argument(
        'dst_label_file',
        help = "The dst label file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.img_root = modify_dir(abs_path(args.img_root))
    print "args: ", args

    ###### get all label file #########
    label_files = get_all_files(args.img_root, backends=[".json"])

    ###### get image size and modify label format  #########
    dst_labels = {}
    for label_file in label_files:
        imgname = os.path.basename(label_file)[:-len(".json")] + ".jpg"
        with open(label_file, "r") as strm:
            src_label = json.loads(strm.read())

        imgpath = os.path.join(args.img_root, imgname)
        if not os.path.exists(imgpath):
            print "{} missing and will skipped!".format(imgpath)
            continue
        img = cv2.imread(imgpath)
        w = img.shape[1]
        h = img.shape[0]

        dst_label = {"text_lines":[], "size":[w, h]}
        for src_box in src_label["Rectangles"]:
            left, right = src_box["X"], src_box["X"] + src_box["Width"] - 1
            top, bottom = src_box["Y"], src_box["Y"] + src_box["Height"] - 1
            dst_box = {
                    "topleft": [left, top], 
                    "topright": [right, top], 
                    "bottomleft": [left, bottom], 
                    "bottomright": [right, bottom], 
                    "text": ""}
            dst_label["text_lines"].append(dst_box)
        dst_labels[imgname] = dst_label

    ###### write to dst label file #########
    dst_lines = []
    for imgname, label in dst_labels.items():
        line = "{}\t{}".format(imgname, json.dumps(label))
        dst_lines.append(line)

    write_lines(args.dst_label_file, dst_lines)

    print "Done."

