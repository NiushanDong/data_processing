#!/bin/bash

src_img_root=/app/dev_user/dataset/id_card/train/subset1_9k
src_img_label=/app/dev_user/dataset/id_card/train/subset1_9k.standard_label

# ************ rotate ****************
tool=/app/dev_user/common_scripts/id_card/rotate_img.py
dst_img_root=/app/dev_user/dataset/id_card/train/subset1_9k_rotate
dst_img_label=/app/dev_user/dataset/id_card/train/subset1_9k_rotate.standard_label
lower_angle=-5
upper_angle=5
rotate_times=1
proc_num=20

cmd="python $tool $src_img_root $src_img_label $src_img_root $dst_img_root \
    $dst_img_label $lower_angle $upper_angle $rotate_times $proc_num"

echo "cmd: $cmd"
eval $cmd
wait

# *********** supplement **************
tool=/app/dev_user/common_scripts/id_card/supplement_img.py
dst_img_root=/app/dev_user/dataset/id_card/train/subset1_9k_supplement
dst_img_label=/app/dev_user/dataset/id_card/train/subset1_9k_supplement.standard_label
lower_ratio=0.0
upper_ratio=0.5
supplement_times=1
proc_num=20

cmd="python $tool $src_img_root $src_img_label $src_img_root $dst_img_root \
    $dst_img_label $lower_ratio $upper_ratio $supplement_times $proc_num"

echo "cmd: $cmd"
eval $cmd
wait
