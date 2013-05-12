#!/usr/bin/env python
#
# draw_tiles.py reads the output of sample_shapes.py and uses it to
# render map tiles for the sampled points.
#
# Input data is assumed to be sorted such that all records for a
# single key (tile) are presented as an uninterrupted sequence. Thus,
# tiles are rendered one at a time as data streams through the
# program.
#

import base64
import csv
import io
import mapnik

from itertools import groupby
from os.path import dirname
from shapely.geometry import box, Point
from sys import path, stdin, stderr

from tilebrute.core import print_status, inc_counter, emit, which, merc_srs

try:
    from gdal2tiles import GlobalMercator
except ImportError:
    # look for gdal2tiles in the system path
    p = which('gdal2tiles.py')
    if p:
        path.append(dirname(p))
        from gdal2tiles import GlobalMercator
    else:
        print_status('Unable to locate gdal2tiles.py in PYTHONPATH or PATH. Aborting.')
        raise 

# quadkey[zoom -z]
# quadkey[levelOfDetail -i]

# geo helpers

def tile_to_meters_Box2d(tile):
    """
    From a 'tile string' of the form tx,ty,zoom', create a mapnik.Box2d
    corresponding to that tile's extend in meters.
    """
    merc = GlobalMercator()
    tx,ty,z = [int(x) for x in tile.split(',')]
    tx,ty = merc.GoogleTile(tx,ty,z)
    return mapnik.Box2d(*merc.TileBounds(tx, ty, z))

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
        bbox = box(query.bbox.minx, query.bbox.miny, query.bbox.maxx, query.bbox.maxy)
        return mapnik.PythonDatasource.wkb_features(
            keys = (),
            features = TuplesDatasource._points(bbox)
        )

# job code

def encode_image(im):
    s = base64.encodestring(im.tostring('png'))
    return s.replace('\n','')

def get_zoom(tile):
    (tx,ty,z) = tile.split(",")
    return int(z)

def opacity(zoom):
    return zoom * 0.05

def pointWeight(zoom):
    if zoom == 4:
        return 0.05333
    elif zoom == 5:
        return 0.08
    elif zoom == 6:
        return 0.12
    elif zoom == 7:
        return 0.18
    elif zoom == 8:
        return 0.27
    elif zoom == 9:
        return 0.405
    elif zoom == 10:
        return 0.6075
    elif zoom == 11:
        return 0.91125
    elif zoom == 12:
        return 1.366875
    elif zoom == 13:
        return 2.0503125
    elif zoom == 14:
        return 3.07546875
    elif zoom == 15:
        return 4.61320312
    elif zoom == 16:
        return 6.9198046
    elif zoom == 17:
        return 10.37970

def read_points(file):
    reader = csv.reader(file, delimiter="\t", strict=True)
    valid_input = 0
    for rec in reader:
        if valid_input == 10000:
            inc_counter("read_points", "valid_input", valid_input)
            valid_input = 0
        if len(rec) != 3:
            inc_counter("read_points", "invalid_input")
            continue
        valid_input += 1
        yield (rec[0],float(rec[1]),float(rec[2]))
    inc_counter("read_points", "valid_input", valid_input)

def init_map(zoom, seq):
    m = mapnik.Map(256, 256, merc_srs)
    m.background_color = mapnik.Color('white')
    s = mapnik.Style()
    r = mapnik.Rule()
    sym = mapnik.MarkersSymbolizer()
    sym.fill = mapnik.Color('black')
    sym.spacing = 0.0
    sym.opacity = opacity(zoom)
    sym.height = mapnik.Expression(str(pointWeight(zoom)/2.0))
    sym.width = mapnik.Expression(str(pointWeight(zoom)/2.0))
    sym.allow_overlap = True
    r.symbols.append(sym)
    s.rules.append(r)
    m.append_style('point_style', s)
    TuplesDatasource.set_source(seq)
    ds = mapnik.Python(factory='TuplesDatasource')
    layer = mapnik.Layer('file', merc_srs)
    layer.datasource = ds
    layer.styles.append('point_style')
    m.layers.append(layer)
    return m

def main():
    for tile,points in groupby(read_points(stdin), lambda x: x[0]):
        zoom = get_zoom(tile)
        map = init_map(zoom, points)
        map.zoom_all()
        im = mapnik.Image(256,256)
        mapnik.render(map,im)
        emit(tile, encode_image(im))

if __name__=='__main__':
    main()
