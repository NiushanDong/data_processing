import os
import sys

src_file = sys.argv[1]
step = int(sys.argv[2])
dst_file = "{}.step{}".format(src_file, step)

src_num = 0
dst_num = 0
with open(src_file, "r") as strm_src, open(dst_file, "w") as strm_dst:
    for i, line in enumerate(strm_src.readlines()):
        src_num += 1
        if i % step == 0:
            strm_dst.write(line)
            dst_num += 1

print "src line number: ", src_num
print "dst line number: ", dst_num

print "Done."
