import os
import sys
import argparse
import time
import shutil


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


def del_list_items_by_keywords(src_list, keyword):
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


def list_intersection(list1, list2):
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
        ret = list_intersection(ret, all_lists[i])
    
    return ret


def list_sub(list1, list2):
    if list1 is None or list2 is None:
        return list1

    ret = []
    for one in list1:
        if not one in list2:
            ret.append(one)
    return ret


def uniform_split_list(src_list, part_num):
    ret = []
    for i in range(part_num):
        ret.append(src_list[i::part_num])

    return ret


def change_dtype(data, dtype):
    if data is None or dtype is None:
        return data

    cmd = "{}(data)".format(dtype)
    data = eval(cmd)

    return data


if __name__ == "__main__":
    pass
