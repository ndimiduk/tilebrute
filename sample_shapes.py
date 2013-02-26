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

_merc = GlobalMercator()
_zooms = (16,17,)

def make_point(x, y):
    return ogr.Geometry(wkt="POINT(%f %f)" % (x, y))

def bbox(geom):
    ll = float("inf")
    bb = float("inf")
    rr = float("-inf")
    tt = float("-inf")

    hull = geom.ConvexHull()
    if not hull:
        inc_counter("bbox", "invalid hull")
        return None
    boundary = hull.GetBoundary()
    if not boundary:
        inc_counter("bbox", "invalid boundary")
        return None
    points = boundary.GetPoints()
    if not points:
        inc_counter("bbox", "invalid points")
        return None

    for x, y in points:
        ll = min(ll, x)
        rr = max(rr, x)
        bb = min(bb, y)
        tt = max(tt, y)

    return (ll,bb,rr,tt)

# job code

def read_feature(file):
    reader = csv.reader(file, strict=True)
    for row in reader:
        if row[0].lower() == "wkt":
            inc_counter("read_feature", "skipped_lines")
            continue
        inc_counter("read_feature", "feature_count")
        geom = ogr.Geometry(wkt=row[0])
        if not geom:
            inc_counter("read_feature", "invalid_geom")
            continue
        yield (geom, int(row[8]))

def sample_geometry(geom, count):
#    with open('/tmp/shape.csv', 'w') as f:
#        w = csv.writer(f, dialect='excel-tab')
#        w.writerow(['wkt'])
#        w.writerow([geom])
#    with open('/tmp/samples.csv', 'w') as f:
#        w = csv.writer(f, dialect='excel-tab')
#        w.writerow(['wkt'])
    ll,bb,rr,tt = bbox(geom)
    point = None
    for i in range(count):
        while True:
            point = make_point(uniform(ll, rr), uniform(bb, tt))
            if geom.Contains(point):
                inc_counter("sample_geometry", "success_sample")
                break
            else:
                inc_counter("sample_geometry", "fail_sample")
#        w.writerow([point])
        yield (point.GetX(), point.GetY())

def latlng_to_tilep(lat, lng, zoom):
    mx, my = _merc.LatLonToMeters(lat, lng)
    px, py = _merc.MetersToPixels(mx, my, zoom)
    tx, ty = _merc.PixelsToTile(px, py)
    tile = _merc.QuadTree(tx, ty, zoom)
    x = int(round(px - (tx * _merc.tileSize)))
    y = int(round(py - (ty * _merc.tileSize)))
    return (tile,x,y)

def make_kv(lng, lat, sep="\t"):
    for z in _zooms:
        hash,px,py = latlng_to_tilep(lat, lng, z)
        key = hash
        value = "%s%s%s" % (px,sep,py)
        yield (key, value)

if __name__=='__main__':
    for geom, population in read_feature(stdin):
        for lng, lat in sample_geometry(geom, population):
            for key, val in make_kv(lng=lng, lat=lat):
                emit(key, val)
