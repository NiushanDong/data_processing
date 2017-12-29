from util_func import *
import json
import argparse
import cv2
from opencv_wrapper import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "in_images",
        help="The image list file or image folder."
    )
    parser.add_argument(
        "img_root",
        help="The root dir of image."
    )
    parser.add_argument(
        "label_root",
        help="The root dir of label file."
    )
    parser.add_argument(
        "dst_label_file",
        help="The output label file."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    in_images = abs_path(args.in_images)
    img_root = modify_dir(abs_path(args.img_root))
    label_root = modify_dir(abs_path(args.label_root))
    dst_label_file = abs_path(args.dst_label_file)

    # read image from image list
    all_imgs = get_imgs(in_images)
    
    # get label from file
    dst_lines = []
    for img_path in all_imgs:
        img_name = os.path.basename(img_path)
        pos = img_name.rfind(".")
        label_name = img_name[:pos] + ".json"
        label_path = os.path.join(label_root, label_name)
        if not os.path.exists(label_path):
            print "label file: \"{}\" not exists".format(label_path)
            continue

        with open(label_path, "r") as strm:
            label = json.loads(strm.read())
        all_points = []
        for i in range(4):
            all_points.append((label["Points"][i]["X"], label["Points"][i]["Y"]))
        all_points = arrange_angular(all_points)
        
        img = cv2.imread(img_path)
        
        label = {   
                    "size":(img.shape[1], img.shape[0]), 
                    "angular_points":{
                        "topleft":all_points[0], "topright":all_points[1], 
                        "bottomleft":all_points[2], "bottomright":all_points[3]
                    }  
                }
        subpath = img_path[len(img_root):]
        dst_line = "{}\t{}".format(subpath, json.dumps(label))
        dst_lines.append(dst_line)
    
    # write label to dst file
    write_lines(dst_label_file, dst_lines)

    print "Done."
