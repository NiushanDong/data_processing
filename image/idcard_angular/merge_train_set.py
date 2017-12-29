from util_func import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "list_file",
        help="The file of subset list."
    )
    parser.add_argument(
        "img_root",
        help="The root dir of images."
    )
    parser.add_argument(
        "out_file",
        help="The output image list."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    list_file = abs_path(args.list_file)
    img_root = modify_dir(abs_path(args.img_root))
    out_file = abs_path(args.out_file)
    
    # get all subsets
    all_subsets = {}
    lines = read_lines(list_file)
    for line in lines:
        contents, parter = split_line(line)
        all_subsets[contents[0]] = contents[1]
    print "Got %d subsets from list file" % len(all_subsets.keys())

    # merge
    dst_lines = []
    for file_path, root_dir in all_subsets.iteritems():
        root_dir = modify_dir(abs_path(root_dir))
        lines = read_lines(file_path)
        for line in lines:
            contents, parter = split_line(line, parter="\t")
            img_path = os.path.join(root_dir, contents[0])
            img_subpath = img_path[len(img_root):]
            dst_line = img_subpath
            for one in contents[1:]:
                dst_line += "\t" + one
            dst_lines.append(dst_line)
    write_lines(out_file, dst_lines)

    print "Totally got {} lines".format(len(dst_lines))
    print "Done."
