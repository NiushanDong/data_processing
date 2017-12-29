from util_func import *
import json
import cv2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'src_label_file',
        help = "The path of src label file"
    )
    parser.add_argument(
        'dst_label_file',
        help = "The path of dst label file"
    )
    parser.add_argument(
        'img_root',
        help = "The root dir or image"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    args.img_root = modify_dir(abs_path(args.img_root))
    print "args: ", args

    dst_lines = []
    for line in read_lines(args.src_label_file):
        contents, _ = split_line(line, parter="\t")
        imgname = contents[0]
        label = json.loads(contents[1])
        imgpath = os.path.join(args.img_root, imgname)
        img = cv2.imread(imgpath)
        size = [img.shape[1], img.shape[0]]
        label["size"] = size
        
        dst_lines.append("{}\t{}".format(imgname, json.dumps(label)))
    write_lines(args.dst_label_file, dst_lines)
    print "Done."
