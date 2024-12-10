import os
import sys
import urllib.request
import multiprocessing
from multiprocessing import Pool
import shutil
import argparse
import time
import pickle


def auto_proc_num(ratio=0.8):
    proc_num = int(multiprocessing.cpu_count() * ratio)
    return proc_num


def path_exist(path):
    if os.path.exists(path):
        return True
    else:
        return False


def  list_group(src_list, num):
    all_parts = []
    for i in range(num):
        all_parts.append([])
    for i, one in enumerate(src_list):
        all_parts[i%num].append(one)
    return all_parts



def list_mean(data_list):
    if data_list is None:
        return None
    data_sum = 0
    for one in data_list:
        data_sum += one
    return float(data_sum) / len(data_list)


def list_subset_by_keywords(src_data, keyword):
    if src_data is None or keyword is None:
        return None

    ret = []
    for data in src_data:
        if not data.find(keyword) == -1:
            ret.append(data)

    return ret


def del_list_items_with_keywords(src_list, keyword):
    if src_list is None or keyword is None:
        return src_list

    ret = []
    for data in src_list:
        if data.find(keyword) == -1:
            ret.append(data)

    return ret


def sort_list(src_data, reverse=False):
    data_num = len(src_data)
    dst_data = src_data
    indexes = list(range(data_num))
    for i in range(data_num-1, 0, -1):
        for j in range(0, i):
            if (not reverse and dst_data[j] > dst_data[j+1])\
                    or (reverse and dst_data[j] < dst_data[j+1]):
                tmp = dst_data[j]
                dst_data[j] = dst_data[j+1]
                dst_data[j+1] = tmp
                tmp = indexes[j]
                indexes[j] = indexes[j+1]
                indexes[j+1] = tmp
    return dst_data, indexes


def dict_min(src_dict):
    if src_dict is None:
        return None, None

    all_keys = src_dict.keys()
    ret_val = src_dict[all_keys[0]]
    ret_key = all_keys[0]
    for key in all_keys:
        if ret_val > src_dict[key]:
            ret_val = src_dict[key]
            ret_key = key

    return ret_key, ret_val


def sets_union(all_sets):
    if all_sets is None:
        return None
    
    ret = set()
    for one_set in all_sets:
        ret = ret | one_set

    return ret


def two_list_intersection(list1, list2):
    if list1 is None or list2 is None:
        return None

    ret = []
    for one in list1:
        if one in list2:
            ret.append(one)

    return ret


def lists_intersection(all_lists):
    if all_lists is None:
        return None

    ret = all_lists[0]
    for i in range(1, len(all_lists)):
        ret = two_list_intersection(ret, all_lists[i])
    
    return ret


def lists_non_shared(all_lists):
    if all_lists is None: 
        return None

    common = lists_intersection(all_lists)
    ret = []
    for one_list in all_lists:
        for data in one_list:
            if not data in common:
                ret.append(data)
    
    return ret


def list_sub(list1, list2):
    if list1 is None or list2 is None:
        return list1

    ret = []
    for one in list1:
        if not one in list2:
            ret.append(one)
    return ret


def erase_enter_end(src_str):
    if src_str.endswith("\r\n"):
        src_str = src_str[:-2]
    elif src_str.endswith("\n"):
        src_str = src_str[:-1]

    return src_str


def uniform_split_list(src_list, part_num):
    ret = []
    for i in range(part_num):
        ret.append(src_list[i::part_num])

    return ret


def try_make_dir(path):
    if not os.path.exists(path) and not path == "":
        os.makedirs(path)


def try_make_dir_multi(path_list):
    for path in path_list:
        try_make_dir(path)


def try_remove(path):
    if path == "":
        return
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print("dir: %s removed" % path)
        else:
            os.remove(path)
            print("file: %s removed" % path)


def try_remove_multi(path_list):
    for path in path_list:
        try_remove(path)


def read_lines(file, erase_end=True, erase_strs=None):
    ret = []
    with open(file, "r") as strm:
        line_set = set()
        for line in strm.readlines():
            if erase_end:
                line = erase_enter_end(line)
            if not erase_strs is None:
                for one in erase_strs:
                    line = line.replace(one, "")
            ret.append(line)

    return ret


def write_lines(file_path, lines, add_end=True, create_folder=False, append_line=False):
    # create folder
    if create_folder:
        file_dir = os.path.dirname(file_path)
        try_make_dir(file_dir)

    strm = open(file_path, "w") if not append_line else open(file_path, "a")
    for line in lines:
        line = line+"\n" if add_end else line
        strm.write(line)
    strm.close()


def write_lists(file_path, data_all, parter=" "):
    if data_all is None:
        return
    try_make_dir(os.path.dirname(file_path))
    all_lines = []
    for data in data_all:
        if data is None:
            continue
        all_lines.append(parter.join(data))

    write_lines(file_path, all_lines)


def erase_repeat(src_list):
    if src_list is None:
        return None
    data_set = set(src_list)
    ret = []
    for one in data_set:
        ret.append(one)

    return ret


def read_pkl(file_path):
    if file_path is None or not os.path.exists(file_path):
        print("{} not exists".format(file_path))
        return None

    with open(file_path, "rb") as strm:
        ret = pickle.load(strm)

    return ret


def write_pkl(file_path, data):
    if file_path is None or data is None:
        return
    try_make_dir(os.path.dirname(file_path))
    with open(file_path, "wb") as strm:
        pickle.dump(data, strm)


def split_line(line, parter=None):
    if not parter is None:
        contents = line.split(parter)
        return contents, parter

    if not line.find("\t") == -1:
        contents = line.split("\t")
        parter = "\t"
    elif not line.find(" ") == -1:
        contents = line.split(" ")
        parter = " "
    else:
        contents = [line]
        parter = None
    return contents, parter


def download_imgs(pairs):
    for i, pair in enumerate(pairs):
        if i % 1000 == 0:
            print("downloaded %d images" % (i+1))
        try:
            url = pair[0]
            print("url: ", url)
            dst_path = pair[1]
            dst_dir = os.path.dirname(dst_path)
            try_make_dir(dst_dir)
            request.urlretrieve(url, dst_path)
        except Exception as err:
            print(err)


def download_imgs_parallel(pairs, proc_num):
    all_parts = []
    for i in range(proc_num):
        all_parts.append([])
    for i, one in enumerate(pairs):
        all_parts[i%proc_num].append(one)
    pool = Pool(proc_num)
    pool.map(download_imgs, all_parts)


def get_all_files(root_dir, backends=None):
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if not backends is None:
                for one in backends:
                    if file.endswith(one):
                        file = os.path.join(root, file)
                        all_files.append(file)
            else:
                file = os.path.join(root, file)
                all_files.append(file)
    for i, one in enumerate(all_files):
        all_files[i] = abs_path(one)
    return all_files


def get_imgs_in_folder(folder, 
        backends=[".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".bmp", ".BMP"]):
    ret = get_all_files(folder, backends)
    return ret


def get_imgs(path, img_root=None):
    imgs = []
    if os.path.isdir(path):
        imgs = get_imgs_in_folder(path)
    else:
        lines = read_lines(path)
        for line in lines:
            contents, parter = split_line(line)
            img_path = os.path.join(img_root, contents[0]) \
                    if not img_root is None else contents[0]
            imgs.append(contents[0])
    for i, one in enumerate(imgs):
        imgs[i] = abs_path(one)
    return imgs


def append_str_to_imgname(img_path, prefix=None, postfix=None):
    if not prefix is None:
        img_path = prefix + img_path
    if not postfix is None:
        pos = img_path.rfind(".")
        if pos == -1:
            img_path += postfix
        else:
            img_path = img_path[:pos] + postfix + img_path[pos:]
    return img_path


def replace_root(src_path, src_root, dst_root):
    if src_path.find(src_root) == -1:
        print("replace_root() ==> src_root not find in src_path")
        return None
    modify_dir(src_root)
    modify_dir(dst_root)
    dst_path = src_path.replace(src_root, dst_root)
    return dst_path


def abs_path(path):
    if path == "":
        return ""
    return os.path.abspath(path)


def modify_dir(dir_path):
    if dir_path == "":
        return dir_path
    if not dir_path.endswith("/"):
        dir_path += "/"
    return dir_path


def decode_gif(all):
    for one in all:
        gif_file = one[0]
        img_dir = one[1]
        max_frames = one[2]
        try_make_dir(img_dir)
        os.system("./gif2images {} {} {}".format(gif_file, img_dir, max_frames))


def move_file(src_path, dst_path):
    if not os.path.exists(src_path):
        return
    dst_dir = os.path.dirname(dst_path)
    try_make_dir(dst_dir)
    shutil.move(src_path, dst_path)


def copy_file(src_path, dst_path):
    if not os.path.exists(src_path):
        return
    dst_dir = os.path.dirname(dst_path)
    try_make_dir(dst_dir)
    shutil.copy(src_path, dst_path)


def change_dtype(data, dtype):
    if data is None or dtype is None:
        return data

    cmd = "{}(data)".format(dtype)
    data = eval(cmd)

    return data


if __name__ == "__main__":
    write_pkl("2.pkl", None)
    print("read: ", read_pkl("2.pkl"))
    sys.exit()
    data = [4, 5, 2, 8, 1, 0, 3, 4]
    print(data)
    data, indexes = sort_list(data, reverse=True)
    print(data)
    print(indexes)
    data = change_dtype(1, "str")
    print(data, type(data))

