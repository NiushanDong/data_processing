import os
import sys
import json
import shutil
from xml.dom.minidom import Document
import cv2
from util_func import *
from opencv_wrapper import *
import pprint 
import ipdb


def parse_args():
    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        "--subset",
        default="",
        help="the subset name."
    )
    parser.add_argument(
        "--remove_old", 
        default=1,
        help="set as 1 if remove old result"
    )
    parser.add_argument(
        "--save_anno_img", 
        default=0,
        help="set 1 if draw annotation"
    )
    parser.add_argument(
        "--start_idx", 
        default="1", 
        help="the start index of output image"
    )
    parser.add_argument(
        "--min_size", 
        default=600, 
        help="the min size of image"
    )
    parser.add_argument(
        "--max_size", 
        default=1200, 
        help="the max size of image"
    )
    parser.add_argument(
        "--step", 
        default=16, 
        help="the step of box splitting"
    )

    return parser.parse_args()

def limit(data, lower, upper):
    if data > upper:
        data = upper
    elif data < lower:
        data = lower
    return data

def modify_box(box, img_width, img_height):
    box[0] = limit(box[0], 0, img_width-1)
    box[1] = limit(box[1], 0, img_width-1)
    box[2] = limit(box[2], 0, img_height-1)
    box[3] = limit(box[3], 0, img_height-1)
    return box

def write_img_annotation(xml_file_path, boxes, img_w, img_h):
    doc = Document()
    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)
    size = doc.createElement('size')
    width = doc.createElement('width')
    width_text = doc.createTextNode(str(img_w))
    width.appendChild(width_text)
    height = doc.createElement('height')
    height_text = doc.createTextNode(str(img_h))
    height.appendChild(height_text)
    depth = doc.createElement('depth')
    depth_text = doc.createTextNode(str(3))
    depth.appendChild(depth_text)
    size.appendChild(width)
    size.appendChild(height)
    size.appendChild(depth)
    annotation.appendChild(size)
    
    for box in boxes:
        object = doc.createElement('object')
        
        name = doc.createElement('name')
        name.appendChild(doc.createTextNode("text"))
        object.appendChild(name)
        
        bndbox = doc.createElement('bndbox')
        object.appendChild(bndbox)
        xmin = doc.createElement("xmin")
        xmin.appendChild(doc.createTextNode(str(int(box[0]))))
        xmax = doc.createElement("xmax")
        xmax.appendChild(doc.createTextNode(str(int(box[1]))))
        ymin = doc.createElement("ymin")
        ymin.appendChild(doc.createTextNode(str(int(box[2]))))
        ymax = doc.createElement("ymax")
        ymax.appendChild(doc.createTextNode(str(int(box[3]))))
        bndbox.appendChild(xmin)
        bndbox.appendChild(ymin)
        bndbox.appendChild(xmax)
        bndbox.appendChild(ymax)
        annotation.appendChild(object)

    with open(xml_file_path, "w") as strm:
        strm.write(doc.toprettyxml(indent='\t', encoding='utf-8'))


if __name__ == "__main__":
    args = parse_args()
    print "args: ", args
    label_file = abs_path(args.label_file)
    out_root = modify_dir(abs_path(args.out_root))
    src_img_root = modify_dir(abs_path(args.img_root))
    subset = args.subset
    start_idx = int(args.start_idx)
    min_size = int(args.min_size)
    max_size = int(args.max_size)
    split_step = int(args.step)

    anno_root = os.path.join(out_root, "Annotations", subset)
    dst_img_root = os.path.join(out_root, "JPEGImages", subset)
    imgset_path = os.path.join(out_root, "ImageSets", subset+".txt")
    anno_img_root = os.path.join(out_root, "AnnotationJPEGImages", subset)

    if int(args.remove_old) == 1:
        try_remove_multi([anno_root, dst_img_root, imgset_path, anno_img_root])
    try_make_dir_multi([anno_root, dst_img_root, os.path.dirname(imgset_path), 
            anno_img_root])
    
    # read from src file
    all_img_boxes = {}
    lines = read_lines(label_file)
    for line in lines:
        contents, parter = split_line(line, parter="\t")
        src_img_path = os.path.join(src_img_root, contents[0])
        dst_boxes = []
        for box in json.loads(contents[1])["text_lines"]:
            all_x = [
                    box["topleft"][0], box["topright"][0], 
                    box["bottomleft"][0], box["bottomright"][0]]
            all_y = [
                    box["topleft"][1], box["topright"][1], 
                    box["bottomleft"][1], box["bottomright"][1]]
            dst_boxes.append([min(all_x), max(all_x), min(all_y), max(all_y)])
        all_img_boxes[src_img_path] = dst_boxes
    print "Got %d images from label file" % len(all_img_boxes.keys())
    
    dst_img_idx = start_idx
    imgset = []
    for src_img_path, boxes in all_img_boxes.items():
        # resize image
        img = cv2.imread(src_img_path)
        shorter = min(img.shape[0], img.shape[1])
        longer = max(img.shape[0], img.shape[1])
        scale = float(min_size) / shorter
        if longer * scale > max_size:
            scale = float(max_size) / longer
        img = cv2.resize(
                img, None, None, fx=scale, fy=scale, 
                interpolation=cv2.INTER_LINEAR)
        imgname = os.path.basename(src_img_path)
        dst_img_path = os.path.join(dst_img_root, "%08d_%s.jpg"%(dst_img_idx, imgname))
        write_img(dst_img_path, img)

        # convert box locations
        for i in range(len(boxes)):
            for j in range(4):
                boxes[i][j] = int(scale * boxes[i][j])

        # split box to multi
        boxes_split = []
        for box in boxes:
            end = 0
            for left in range(box[0], box[1]+1, split_step):
                boxes_split.append([left, left+split_step, box[2], box[3]])
                end = left + split_step
            if end < box[1] + 1:
                boxes_split.append([end, end+split_step, box[2], box[3]])
        for i, box in enumerate(boxes_split):
            boxes_split[i] = modify_box(box, img.shape[1], img.shape[0])
        
        # write annotation file
        anno_file = os.path.join(anno_root, "%08d_%s.xml"%(dst_img_idx, imgname))
        write_img_annotation(anno_file, boxes_split, img.shape[1], img.shape[0])
        imgset.append("%s/%08d_%s" % (subset, dst_img_idx, imgname))

        # draw annotation on image
        if int(args.save_anno_img) == 1:
            for box in boxes_split:
                img = draw_polygon(img, 
                        [   (box[0], box[2]), (box[1], box[2]), 
                            (box[1], box[3]), (box[0], box[3])])
            write_img(os.path.join(anno_img_root, imgname), img)

        dst_img_idx += 1

    write_lines(imgset_path, imgset)

print "Done."
