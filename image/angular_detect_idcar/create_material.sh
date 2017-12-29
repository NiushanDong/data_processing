#!/bin/bash

set -e
set -u

in_data_root=/app/dev_user/dataset/id_card/train
out_data_root=/app/dev_user/dataset/id_card/material_train

generate_mask=1
create_db=1
hdf5_with_img=0
create_img_lmdb=1
create_mask_lmdb=1
resize_w=224
resize_h=224
mask_fg_val=1

lmdb_tool=/app/dev_user/projects/caffe-master/build/tools/convert_imageset
mask_script=/app/dev_user/common_scripts/id_card/generate_mask.py
db_script=/app/dev_user/common_scripts/id_card/create_dataset.py

label_file=$in_data_root/all_train.standard_label
img_root=$in_data_root
mask_img_root=$out_data_root/train.all_train.mask

# generate mask image
if [ $generate_mask == 1 ]; then
    cmd="python $mask_script $label_file $mask_img_root $resize_w $resize_h \
        --img_root=$img_root --forground_val=$mask_fg_val"
    echo -e "cmd: $cmd"
    eval $cmd
fi

# write to db
if [ $create_db == 1 ]; then
    pos_hdf5=$out_data_root/train.all_train.pos.hdf5
    if [ $create_img_lmdb == 1 ]; then
        img_lmdb=$out_data_root/train.all_train.lmdb
    else
        img_lmdb=""
    fi
    if [ $create_mask_lmdb == 1 ]; then
        mask_lmdb=$out_data_root/train.all_train.mask.lmdb
    else
        mask_lmdb=""
    fi

    cmd="python $db_script $label_file $img_root $mask_img_root $pos_hdf5 \
        --image_db=$img_lmdb --mask_db=$mask_lmdb --hdf5_with_img=$hdf5_with_img \
        --resize_w=$resize_w --resize_h=$resize_h --lmdb_tool=$lmdb_tool"
    echo -e "\ncmd: $cmd"
    eval $cmd
fi

