#!/usr/bin/env python
#
# sample_shapes.py reads CVS input data and produces sampled points
# representing that input.
#
# Input is assumed to be comma-separated, newline-delimited,
# containing a geometry in WKT at field[0] and the population count at
# field[8]. WKT coordinates are assumed to be EPSG:4326. Output
# records are written to stdout as points sampled from the geometry.
# They are line-oriented, one point per record. A record consists of a
# "key", followed by a tab character, followed by a "value". Keys
# define the tile in which the point resides, of the format
# "tilex,tiley,zoom". Values are the sampled point, "mx,my" as meters
# in EPSG:900913. Additional Hadoop control information is printed to
# stderr; it can be safely ignored when running locally.
#

import csv
import ogr

from gdal2tiles import GlobalMercator
from random import uniform
from sys import stdin, stderr, maxsize

# hadoop helpers

def print_status(msg):
    print >> stderr, "reporter:status:%s" % msg

def inc_counter(group, counter):
    print >> stderr, "reporter:counter:_m_%s,%s,1" % (group, counter)

def emit(key, val):
    print "%s\t%s" % (key, val)

# geo helpers

_merc = GlobalMercator()
_zooms = (6,7,8)

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

# increase buffers to account for really big geometries
csv.field_size_limit(maxsize)

def read_feature(file):
    """
    Read a single feature from the input source. Expects to find a geometry
    and a population count. yield (org.Geometry, int(population))
    """
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
    """
    Given a Geometry and count, returns count Points contained by that geom.
    """
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
        yield (point.GetX(), point.GetY())

def make_kv(lat, lng):
    """
    Yield all the Google (tile,x,y)'s for the lng,lat pair at various zoom levels.
    Converts lng,lat into meters.
    """
    for z in _zooms:
        mx,my = _merc.LatLonToMeters(lat, lng)
        tx,ty = _merc.MetersToTile(mx, my, z)
        tx,ty = _merc.GoogleTile(tx,ty,z)
        key = "%d,%d,%d" % (tx,ty,z)
        value = "%0.5f\t%0.5f" % (mx,my)
        yield (key, value)

if __name__=='__main__':
    for geom, population in read_feature(stdin):
        for lng, lat in sample_geometry(geom, population):
            for key, val in make_kv(lat, lng):
                emit(key, val)
