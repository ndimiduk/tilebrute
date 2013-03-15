#!/usr/bin/env python

import base64
import csv
import io
import mapnik

from itertools import groupby
from gdal2tiles import GlobalMercator
from shapely.geometry import box, Point
from sys import stdin, stderr

# quadkey[zoom -z]
# quadkey[levelOfDetail -i]

# hadoop helpers

def print_status(msg):
    print >> stderr, "reporter:status:%s" % msg

def inc_counter(group, counter):
    print >> stderr, "reporter:counter:_r_%s,%s,1" % (group, counter)

def emit(key, val):
    print "%s\t%s" % (key, val)

# geo helpers

# spherical mercator
_merc_srs = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over<>'

def tile_to_meters_Box2d(tile, _merc = GlobalMercator()):
    """
    From a 'tile string' of the form tx,ty,zoom', create a mapnik.Box2d
    corresponding to that tile's extend in meters.
    """
    tx,ty,z = [int(x) for x in tile.split(',')]
    minx,miny,maxx,maxy = _merc.TileBounds(tx, ty, z)
    return mapnik.Box2d(minx, miny, maxx, maxy)

class Peekable:
    """
    Extend an Interable with single-item look-ahead.

    it = Peekable(...)
    for x in it:
        if it.has_next():
            # more coming
            x_plus_one = it.peek()
        else:
            # last one!
    """
    _null = object()

    def __init__(self, it):
        self._it = iter(it)
        self._cache = Peekable._null

    def __iter__(self):
        return self

    def next(self):
        if self._cache is Peekable._null:
            return self._it.next()
        else:
            ret = self._cache
            self._cache = Peekable._null
            return ret

    def peek(self):
        if self._cache is Peekable._null:
            self._cache = self.next()
        return self._cache

    def has_next(self):
        if self._cache is Peekable._null:
            try: self._cache = self.next()
            except StopIteration: return False
            else: return True
        else:
            return True

class TuplesDatasource(mapnik.PythonDatasource):
    """
    Generates mx,my Point data in Google Merc. Reads data points from Iterable
    specified with TuplesDatasource.set_source(), assumed to produce
    tile,mx,my.

    Using a static variable as a dirty hack to get around type erasure of C++
    instances. mapnik.Python(...) converts all constructor args to Strings.
    That means we can't pass an Iterable via the constructor. Worse, the
    object returned is a C++ Datasource instance, oblivious of its Pythonic
    outer shell. With no way to set instance variables on construction and no
    way to update them afterwards, use a static variable to hold the generator
    an instance will consume. As a result, TuplesDatasource is not
    thread-safe. Generous application of asserts serve to protect this
    terrible API from losing data.
    """

    _source = None

    @staticmethod
    def get_source():
        assert TuplesDatasource._source, "TuplesDatasource._source not yet initialized!"
        return TuplesDatasource._source

    @staticmethod
    def set_source(source):
        assert not TuplesDatasource._source or not TuplesDatasource._source.has_next(), "TuplesDatasource._source is not yet empty!"
        TuplesDatasource._source = Peekable(source)

    @staticmethod
    def get_tile():
        tile,_,_ = TuplesDatasource.get_source().peek()
        return tile

    @staticmethod
    def _points(bbox):
        for tile, mx, my in TuplesDatasource.get_source():
            p = Point(mx, my)
            if not bbox.contains(p):
                inc_counter("TuplesDatasource._points", "query_out_of_range")
                continue
            yield (p.wkb, {})

    def __init__(self):
        """
        Create a Datasource over the specified file handle. Be advised, C++
        interop turns everything passed into Strings.

        Beware, instantiation is not initialization. Before instantiating, you
        must seed the souce with TuplesDatasource.set_source(Iterable)
        """
        super(TuplesDatasource, self).__init__()
        # fill in required interface
        self.envelope = tile_to_meters_Box2d(TuplesDatasource.get_tile())
        self.data_type = mapnik.DataType.Vector

    def features(self, query):
        b = query.bbox
        bbox = box(b.minx, b.miny, b.maxx, b.maxy)
        return mapnik.PythonDatasource.wkb_features(
            keys = (),
            features = TuplesDatasource._points(bbox)
        )

# job code

def encode_image(im):
    s = base64.encodestring(im.tostring('png'))
    return s.replace('\n','')

def read_points(file):
    reader = csv.reader(file, delimiter="\t", strict=True)
    for rec in reader:
        if len(rec) != 3:
            inc_counter("read_points", "invalid_input")
            continue
        inc_counter("read_points", "valid_input")
        yield (rec[0],float(rec[1]),float(rec[2]))

def init_map(seq):
    m = mapnik.Map(256, 256, _merc_srs)
    m.background_color = mapnik.Color('white')
    s = mapnik.Style()
    r = mapnik.Rule()
    r.symbols.append(mapnik.PointSymbolizer())
    s.rules.append(r)
    m.append_style('point_style', s)
    TuplesDatasource.set_source(seq)
    ds = mapnik.Python(factory='TuplesDatasource')
    layer = mapnik.Layer('file', _merc_srs)
    layer.datasource = ds
    layer.styles.append('point_style')
    m.layers.append(layer)
    return m

if __name__=='__main__':
    tiles = set()
    for tile,points in groupby(read_points(stdin), lambda x: x[0]):
        assert tile not in tiles, "I've already seen this tile! Is the input sorted? %s %s" % (tile, tiles)
        map = init_map(points)
        map.zoom_all()
        im = mapnik.Image(256,256)
        mapnik.render(map,im)
#        im.save(tile + '.png', 'png')
        emit(tile, encode_image(im))
