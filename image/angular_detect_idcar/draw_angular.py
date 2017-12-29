from util_func import *
from opencv_wrapper import *
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "images_to_proc",
        help="the image list file or image folder."
    )
    parser.add_argument(
        "label_file",
        help="the standard label file."
    )
    parser.add_argument(
        "img_root",
        help="the root dir of input images."
    )
    parser.add_argument(
        "out_root",
        help="the root dir of output."
    )
    return parser.parse_args()

def process():
    global images_to_proc, label_file, img_root, out_root

    # read label from file
    lines = read_lines(label_file)
    all_labels = {}
    for line in lines:
        contents, parter = split_line(line, parter="\t")
        all_labels[contents[0]] = json.loads(contents[1])

    src_img_paths = get_imgs(images_to_proc)
    print "Got {} images".format(len(src_img_paths))
    dst_img_paths = []
    for src_img_path in src_img_paths:
        dst_img_paths.append(replace_root(src_img_path, img_root, out_root))
    dst_img_num = 0
    for img_idx in range(len(src_img_paths)):
        src_img_path = src_img_paths[img_idx]
        dst_img_path = dst_img_paths[img_idx]
        img_subpath = src_img_path[len(img_root):]

        if not all_labels.has_key(img_subpath):
            #print "{} have no label".format(src_img_path)
            continue
        label = all_labels[img_subpath]["angular_points"]
        points = []
        points.append(label["topleft"])
        points.append(label["topright"])
        points.append(label["bottomleft"])
        points.append(label["bottomright"])

        img = cv2.imread(src_img_path)
        draw_points(img, points)
        write_img(dst_img_path, img)
        dst_img_num += 1
    print "Output {} images".format(dst_img_num)

if __name__ == "__main__":
    args = parse_args()
    images_to_proc = modify_dir(abs_path(args.images_to_proc))
    label_file = abs_path(args.label_file)
    out_root = modify_dir(abs_path(args.out_root))
    img_root = modify_dir(abs_path(args.img_root))
    print "images_to_proc: ", images_to_proc
    print "label_file: ", label_file
    print "img_root: ", img_root
    print "out_root: ", out_root
    
    time_s = time.time()
    process()
    time_e = time.time()
    print "Totally takes {} s".format(time_e - time_s)
    print "Done."
