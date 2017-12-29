# -*- coding: utf-8 -*-

from util_func import *
from opencv_wrapper import *
import ipdb
import json


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "src_text_label_file",
        help = "The text label file of src images"
    )
    parser.add_argument(
        "src_angular_label_file",
        help = "The angular label file of src images"
    )
    parser.add_argument(
        'uncropped_img_root',
        help = "The root dir of uncropped images."
    )
    parser.add_argument(
        "dst_label_file",
        help = "The label file of dst images"
    )
    parser.add_argument(
        "--merge_angular",
        default = "0",
        help = "Set as 1 if merge angular with text label"
    )
    return parser.parse_args()


if __name__ == "__main__":
    ########## modify inputs ##############
    args = parse_args()
    args.uncropped_img_root = modify_dir(abs_path(args.uncropped_img_root))
    print "args: ", args
    
    ########## read text label from file ########
    all_src_text_labels = {}
    lines = read_lines(args.src_text_label_file)
    for line in lines:
        contents, _ = split_line(line, parter="\t")
        imgname, src_text_label = contents[0], json.loads(contents[1])
        all_src_text_labels[imgname] = src_text_label

    ########## read angular label from file ###########
    all_src_angular_labels = {}
    lines = read_lines(args.src_angular_label_file)
    for line in lines:
        contents, _ = split_line(line, parter="\t")
        imgname, label = contents[0], json.loads(contents[1])
        all_src_angular_labels[imgname] = label

    ########## map text locations ##########
    for imgname, text_label in all_src_text_labels.items():
        ang_pts = all_src_angular_labels[imgname]["angular_points"]
        ang_pts = [ang_pts["topleft"], ang_pts["topright"], 
                ang_pts["bottomleft"], ang_pts["bottomright"]]
        ang_pts = arrange_angular(ang_pts)
        w = (ang_pts["topright"] - ang_pts["topleft"] 
                + ang_pts["bottomright"] - ang_pts["bottomleft"]) / 2
        h = (ang_pts["bottomleft"] - ang_pts["topleft"] 
                + ang_pts["bottomright"] - ang_pts["topright"]) / 2
        rotate = True if w < h else False

        text_boxes = []
        for box in all_src_text_labels["text_lines"]:
            text_boxes.append(
                    [box["topleft"], box["topright"], 
                    box["bottomleft"], box["bottomright"]])
        

        cropped_img_size = all_src_text_labels[imgname]["size"]

    ########## merge angular label ############

    ######### write all locations to dst label file #########


