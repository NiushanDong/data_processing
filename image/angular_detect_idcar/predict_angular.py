from util_func import *
import sys
sys.path.append("/app/dev_user/projects/caffe-master/python")
import caffe
import cv2
import math
import numpy as np
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path",
        help="The root dir of test image or image list file."
    )
    parser.add_argument(
        "img_root",
        help="The root dir of test image"
    )
    parser.add_argument(
        "angular_file",
        help="The file to write angular points in"
    )
    parser.add_argument(
        "net_file",
        help="The net file"
    )
    parser.add_argument(
        "weights_file",
        help="The model file"
    )
    parser.add_argument(
        "--angular_img_root",
        default = "",
        help="The root dir of images with angulars printed."
    )
    parser.add_argument(
        "--angular_img_postfix",
        default = "",
        help="The postfix of angular image postfix."
    )
    parser.add_argument(
        "--mask_img_root",
        default = "",
        help="The output mask image root dir."
    )
    parser.add_argument(
        "--mask_img_postfix",
        default = "",
        help="The postfix of mask image name."
    )
    parser.add_argument(
        "--angular_layer",
        default="",
        help="The angular coordinates layer name"
    )
    parser.add_argument(
        "--mask_layer",
        default="",
        help="The parsing mask layer name"
    )
    parser.add_argument(
        "--batch_size",
        default=1,
        help="The batch size"
    )
    parser.add_argument(
        "--gpu_id",
        default=0,
        help="The gpu id"
    )
    parser.add_argument(
        "--point_size",
        default=5,
        help="The angular point size"
    )
    return parser.parse_args()

def init_net():
    global net_file, weights_file, batch_size, gpu_id 

    if gpu_id < 0:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(gpu_id)
    net = caffe.Net(net_file, weights_file, caffe.TEST)
    input_h_proto = net.blobs[net.inputs[0]].data.shape[2]
    input_w_proto = net.blobs[net.inputs[0]].data.shape[3]
    net.blobs[net.inputs[0]].reshape(
            batch_size, 3, input_h_proto, input_w_proto)
    return net

def preprocess(batch_img_paths):
    global input_w_proto, input_h_proto
    batch_imgs = []
    mean = [104, 117, 123]
    mean = np.asarray(mean, dtype=np.float32)
    mean = mean[:, np.newaxis, np.newaxis]
    scale = 0.003921568627451
    valid_img_paths = []
    for img_path in batch_img_paths:
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if img is None:
            continue
        img = cv2.resize(img, (input_w_proto, input_h_proto))
        img = img.astype(np.float32)
        img = img.transpose([2,0,1])
        img -= mean
        img *= scale
        batch_imgs.append(img)
        valid_img_paths.append(img_path)
    return batch_imgs, valid_img_paths

def forward_batch(batch_imgs):
    global net, angular_layer, mask_layer
    
    angulars = None
    masks = None

    batch_imgs = np.asarray(batch_imgs)
    net.forward_all(data=batch_imgs)
    if not angular_layer == "":
        angulars = net.blobs[angular_layer].data
    if not mask_layer == "":
        masks = net.blobs[mask_layer].data

    return angulars, masks

def save_mask(masks_to_save):
    for mask_path in masks_to_save.keys():
        mask = masks_to_save[mask_path]
        mask_dir = os.path.dirname(mask_path)
        try_make_dir(mask_dir)
        ret, img = cv2.threshold(masks_to_save[mask_path],0.5,255,cv2.THRESH_BINARY)
        cv2.imwrite(mask_path, img)

def modify_pos(x, y, w, h):
    x = 0 if x < 0 else x
    x = w-1 if x > w-1 else x
    y = 0 if y < 0 else y
    y = h-1 if y > h-1 else y
    return x, y

def save_angulars(angulars):
    global angular_file, point_size
    dst_lines = []
    for img_path in angulars.keys():
        pos = angulars[img_path]["pos"]
        img = cv2.imread(img_path)
        w = img.shape[1]
        h = img.shape[0]
        # convert position
        for i in range(len(pos) / 2):
            pos[2*i] = int(w * pos[2*i])
            pos[2*i+1] = int(h * pos[2*i+1])
            pos[2*i], pos[2*i+1] = modify_pos(pos[2*i], pos[2*i+1], w, h)
        
        topleft = [pos[0], pos[1]]
        topright = [pos[2], pos[3]]
        bottomleft = [pos[4], pos[5]]
        bottomright = [pos[6], pos[7]]
        res = {"angular_points":{"topleft":topleft, "topright":topright, 
                "bottomleft":bottomleft, "bottomright":bottomright}, 
                "size":[w, h]}
        dst_line = img_path + "\t" + json.dumps(res)
        dst_lines.append(dst_line)

        # save image with angular printed
        angular_img_path = angulars[img_path]["angular_img_path"]
        if not angular_img_path is None:
            for i in range(len(pos) / 2):
                cv2.circle(img, (pos[2*i], pos[2*i+1]), point_size, (0, 0, 255), -1)
                try_make_dir(os.path.dirname(angular_img_path))
                cv2.imwrite(angular_img_path, img)

    write_lines(angular_file, dst_lines, append_line=True)


def process(all_imgs):
    global batch_size, img_root, angular_img_root, angular_img_postfix, \
            mask_img_root, mask_img_postfix
    img_num = len(all_imgs)
    
    # split to batches
    batch_num = int(math.ceil(float(img_num) / batch_size))
    all_batches = []
    for i in range(batch_num):
        start = i * batch_size
        end = (i + 1) * batch_size
        end = img_num if end > img_num else end
        all_batches.append(all_imgs[start:end])

    # process by batch
    all_angulars = {}
    for one_batch in all_batches:
        batch_imgs, batch_valid_img_paths = preprocess(one_batch)
        batch_angulars, batch_masks = forward_batch(batch_imgs)

        masks_to_save = {}
        angulars_to_save = {}
        for i, img_path in enumerate(batch_valid_img_paths):
            angulars_to_save[img_path] = {"pos":list(batch_angulars[i]),
                    "angular_img_path": None}
            if not angular_img_root == "":
                angular_img_path = replace_root(img_path, img_root, angular_img_root)
                angular_img_path = append_str_to_imgname(angular_img_path, 
                        postfix=angular_img_postfix)
                angulars_to_save[img_path]["angular_img_path"] = angular_img_path
            if not mask_layer == "" and not mask_img_root == "":
                mask_img_path = img_path.replace(img_root, mask_img_root)
                mask_img_path = append_str_to_imgname(mask_img_path, 
                        postfix=mask_img_postfix)
                masks_to_save[mask_img_path] = batch_masks[i].transpose(1, 2, 0)

        save_mask(masks_to_save)
        save_angulars(angulars_to_save)

def get_imgs(input_path):
    global img_root
    all_imgs = []
    if os.path.isdir(input_path):
        all_imgs = get_imgs_in_folder(input_path)
    else:
        lines = read_lines(input_path)
        for line in lines:
            contents, parter = split_line(line)
            img_path = contents[0]
            if not os.path.exists(img_path):
                img_path = os.path.join(img_root, img_path)
            if not os.path.exists(img_path):
                continue
            all_imgs.append(contents[0])
    print "get_imgs() got %d images" % len(all_imgs)
    return all_imgs

if __name__ == "__main__":
    args = parse_args()
    input_path = abs_path(args.input_path)
    img_root = modify_dir(abs_path(args.img_root))
    print "img_root: ", img_root
    
    mask_img_root = modify_dir(abs_path(args.mask_img_root))
    mask_img_postfix = args.mask_img_postfix
    print "mask_img_root: ", mask_img_root
    print "mask_img_postfix: ", mask_img_postfix

    angular_img_root = modify_dir(abs_path(args.angular_img_root))
    angular_img_postfix = args.angular_img_postfix
    print "angular_img_root: ", angular_img_root
    print "angular_img_postfix: ", angular_img_postfix

    angular_file = abs_path(args.angular_file)
    angular_layer = args.angular_layer
    mask_layer = args.mask_layer
    net_file = abs_path(args.net_file)
    weights_file = abs_path(args.weights_file)
    batch_size = int(args.batch_size)
    gpu_id = int(args.gpu_id)
    point_size = int(args.point_size)

    # remove angular position file
    try_remove(angular_file)

    net = init_net()
    input_h_proto = net.blobs[net.inputs[0]].data.shape[2]
    input_w_proto = net.blobs[net.inputs[0]].data.shape[3]
    
    all_imgs = get_imgs(input_path)
    time_s = time.time()
    process(all_imgs)
    time_e = time.time()
    print "%d images take %f s" %(len(all_imgs), time_e-time_s)

    print "Done."
