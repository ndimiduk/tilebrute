#!/usr/bin/env python
#
# write_tiles.py reads the output of draw_tiles.py and saves them to
# the output file system. This is intended for local testing; use
# MapTileOutputFormat for real MR runs.
#
# reads key,value output from the reducer and writes tiles to a path
# rooted at $WRITE_TILES_OUT. Output is of the format {z}/{x}/{y}.png
#

import base64
import csv
import os
from sys import stdin, stderr

def read_records(file):
    reader = csv.reader(file, delimiter="\t", strict=True)
    for rec in reader:
        if len(rec) != 2:
            continue
        (tx,ty,z) = rec[0].split(",")
        path = os.path.join(os.getenv("WRITE_TILES_OUT", "out"), z, tx, ty + ".png")
        blob = base64.decodestring(rec[1])
        yield (path, blob)

def write_file(path, blob):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w+') as f:
        f.write(blob)

if __name__=='__main__':
    for (path, blob) in read_records(stdin):
        write_file(path, blob)
