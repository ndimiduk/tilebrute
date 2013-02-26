#!/usr/bin/env python

import csv
import ogr

from gdal2tiles import GlobalMercator
from random import uniform
from sys import stdin, stderr

# hadoop helpers

def print_status(msg):
    print >> stderr, "reporter:status:%s" % msg

def inc_counter(group, counter):
    print >> stderr, "reporter:counter:%s,%s,1" %(group, counter)

def emit(key, val):
    print "%s\t%s" % (key, val)

# geo helpers

def quadkey_to_tileXY(quadkey):
    tx = 0
    ty = 0
    zoom = len(quadkey)

    for z in reversed(range(zoom)):
        mask = 1 << z
        if quadkey[z] == '0':
            break
        elif quadkey[z] == '1':
            tx |= mask
        elif quadkey[z] == '2':
            ty |= mask
        elif quadkey[z] == '3':
            tx |= mask
            ty |= mask
    return (tx,ty,zoom)

_point_weight = {
    4: 0.05333,
    5: 0.08,
    6: 0.12,
    7: 0.18,
    8: 0.27,
    9: 0.405,
    10: 0.6075,
    11: 0.91125,
    12: 1.366875,
    13: 2.0503125,
    14: 3.07546875,
    15: 4.61320312,
    16: 6.9198046,
    17: 10.37970
    }

# job code

def read_points(file):
    reader = csv.reader(file, delimiter="\t", strict=True)
    for rec in reader:
        if len(rec) != 3:
            inc_counter("read_points", "invalid_input")
        yield (rec[0],float(rec[1]),float(rec[2]))

def append_point(tile, lat, lng):
    if not tile:
        tile = Image()
        tile.size = (512,512)

if __name__=='__main__':
    prev_hash = None
    for hash,lat,lng in read_points(stdin):
        if prev_hash and prev_hash != hash:
            raise Exception("reducer key missmatch!")
        prev_hash = hash
        
