import pickle as pkl
import os
import sys

file_path = sys.argv[1]
with open(file_path, "rb") as strm:
    print pkl.load(strm)
