import os
import sys
import json
import shutil
from xml.dom.minidom import Document
import cv2
from util_func import *
from opencv_wrapper import *
import pprint 


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
        action="store_true",
        help="set as 1 if remove old result"
    )
    parser.add_argument(
        "--start_idx", 
        default="1", 
        help="the start index of output image"
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
    box[1] = limit(box[1], 0, img_height-1)
    box[2] = limit(box[2], 0, img_width-box[0]+1)
    box[3] = limit(box[3], 0, img_height-box[1]+1)
    return box

def filter_box(box, img_w, img_h):
    w = box[2]
    h = box[3]
    if img_w <= 0 or img_h <= 0:
        return False
    else:
        return True


if __name__ == "__main__":
    args = parse_args()
    print "args: ", args
    label_file = abs_path(args.label_file)
    out_root = modify_dir(abs_path(args.out_root))
    img_root = modify_dir(abs_path(args.img_root))
    subset = args.subset
    remove_old = args.remove_old
    start_idx = int(args.start_idx)

    dst_img_root = modify_dir(os.path.join(out_root, "JPEGImages/"+subset))
    annotation_root = modify_dir(os.path.join(out_root, "Annotations/"+subset))
    
    # read from src file
    file_boxes = {}
    lines = read_lines(label_file)
    for line in lines:
        contents, parter = split_line(line, parter="\t")
        src_img_path = os.path.join(img_root, contents[0])
        dst_boxes = []
        for box in json.loads(contents[1])["text_lines"]:
            x = box["topleft"][0]
            y = box["topleft"][1]
            w = box["bottomright"][0] - x + 1
            h = box["bottomright"][1] - y + 1

            dst_boxes.append((x, y, w, h, "text"))
        file_boxes[src_img_path] = dst_boxes
    print "Got %d images from label file" % len(file_boxes.keys())
    
    # copy images and create annotation files
    if remove_old:
        os.system("rm -rf {} {}".format(dst_img_root, annotation_root))
        print "old removed"
    if not os.path.exists(dst_img_root):
        os.makedirs(dst_img_root)
    if not os.path.exists(annotation_root):
        os.makedirs(annotation_root)
    
    valid_box_num = 0
    invalid_box_num = 0
    for img_idx, src_img_path in enumerate(file_boxes.keys()):
        dst_img_name = "%08d.jpg" % (img_idx + start_idx)
        dst_img_path = os.path.join(dst_img_root, dst_img_name)
        
        # create annotation file
        xml_file_name = "%08d.xml" % (img_idx + start_idx)
        xml_file_path = os.path.join(annotation_root, xml_file_name)
        doc = Document()
        annotation = doc.createElement('annotation')
        doc.appendChild(annotation)
        
        size = doc.createElement('size')
        img = cv2.imread(src_img_path, cv2.IMREAD_COLOR)
        if img is None:
            print "Read image {} failed and skiped"
            continue
    
        # write annotation
        width = doc.createElement('width')
        width_text = doc.createTextNode(str(img.shape[1]))
        width.appendChild(width_text)
        height = doc.createElement('height')
        height_text = doc.createTextNode(str(img.shape[0]))
        height.appendChild(height_text)
        depth = doc.createElement('depth')
        depth_text = doc.createTextNode(str(img.shape[2]))
        depth.appendChild(depth_text)
        size.appendChild(width)
        size.appendChild(height)
        size.appendChild(depth)
        annotation.appendChild(size)
    
        boxes = file_boxes[src_img_path]
        have_box = False
        for box in boxes:
            box = [int(box[i]) for i in range(4)]
            box = modify_box(box, img.shape[1], img.shape[0])
            if not filter_box(box, img.shape[1], img.shape[0]):
                print "src_img_path: ", src_img_path
                print "box: ", box
                print "image shape: ", img.shape
                print "Invalid box and will be skipped"
                invalid_box_num += 1
                continue
            object = doc.createElement('object')
            
            name = doc.createElement('name')
            name.appendChild(doc.createTextNode("text"))
            object.appendChild(name)
            
            bndbox = doc.createElement('bndbox')
            object.appendChild(bndbox)
            xmin = doc.createElement("xmin")
            xmin.appendChild(doc.createTextNode(str(int(box[0]))))
            ymin = doc.createElement("ymin")
            ymin.appendChild(doc.createTextNode(str(int(box[1]))))
            xmax = doc.createElement("xmax")
            xmax.appendChild(doc.createTextNode(str(int(box[0]+box[2]-1))))
            ymax = doc.createElement("ymax")
            ymax.appendChild(doc.createTextNode(str(int(box[1]+box[3]-1))))
            bndbox.appendChild(xmin)
            bndbox.appendChild(ymin)
            bndbox.appendChild(xmax)
            bndbox.appendChild(ymax)
            annotation.appendChild(object)
    
            valid_box_num += 1
            have_box = True
        if not have_box:
            print "%s have no box" % src_img_path
            continue
        
        # write image to dst folder
        write_img(dst_img_path, img)
        
        with open(xml_file_path, "w") as strm:
            strm.write(doc.toprettyxml(indent='\t', encoding='utf-8'))
    print "Totally got %d valid boxes" % valid_box_num
    print "Totally skipped %d invalid boxes" % invalid_box_num
    
    print "Done."
