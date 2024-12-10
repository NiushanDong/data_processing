import os
import sys
sys.path.append(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../utils/python"))
from util import *
import h5py

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "h5_file",
        help="The path of hdf5 file."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    h5_file = os.path.abspath(args.h5_file)
    h5_strm = h5py.File(h5_file, "r")
    keys = h5_strm.keys()
    print "hdf5 keys: ", keys
    for key in keys:
        data = h5_strm[key]
        print "{} data: {}".format(key, data[:])
        print "{} data shape: {}".format(key, data.shape)
    print "Done."
