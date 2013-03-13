#!/usr/bin/env python

import base64
import csv
import io
import mapnik

from gdal2tiles import GlobalMercator
from shapely.geometry import box, Point
from sys import stdin, stderr

# quadkey[zoom -z]
# quadkey[levelOfDetail -i]

# hadoop helpers

def log(msg):
    print >> stderr, msg

def print_status(msg):
    print >> stderr, "reporter:status:%s" % msg

def inc_counter(group, counter):
    print >> stderr, "reporter:counter:%s,%s,1" %(group, counter)

def emit(key, val):
    print "%s\t%s" % (key, val)

# geo helpers

_merc = GlobalMercator()
# spherical mercator
_merc_srs = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over<>'
#_merc_srs = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over'

def max_coord(zoom):
    return 256 * ((2**zoom) -1)

def quadkey_to_tile_Box2d(quadkey):
    tx,ty,zoom = quadkey_to_tileXY(quadkey)
    minx,miny,maxx,maxy = _merc.TileBounds(tx, ty, zoom)
    return mapnik.Box2d(minx, miny, maxx, maxy)

def tile_to_meters_Box2d(tile):
    tx,ty,z = [int(x) for x in tile.split(',')]
    minx,miny,maxx,maxy = _merc.TileBounds(tx, ty, z)
    b2d = mapnik.Box2d(minx, miny, maxx, maxy)
    log("tile_to_meters_Box2d(%s) -> %s" % (tile, b2d))
    return b2d

class DatasourceError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class TuplesDatasource(mapnik.PythonDatasource):
    """
    Generates mx,my Point data in Google Merc. Reads data points from `fid`
    source, assumed to be CSV of tile,mx,my.
    """

    #
    # using a static variable as a dirty hack to get data out of the
    # Datasource instance.
    #
    _tile = None

    @staticmethod
    def _get_tile():
        if not TuplesDatasource._tile:
            raise DatasourceError("TuplesDatasource._tile not yet set!")
        return TuplesDatasource._tile

    @staticmethod
    def _set_tile(tile):
        if TuplesDatasource._tile:
            raise DatasourceError("TuplesDatasource._tile already set!")
        TuplesDatasource._tile = tile

    def __init__(self, fid, closefd=''):
        """
        Create a Datasource over the specified file handle. Be advised, C++
        interop turns everything passes into Strings.
        """
        log("TuplesDatasource.__init__(%s, %s)" % (fid, closefd))

        # create a buffered reader over the file handle
        reader = io.BufferedReader(io.open(int(fid), mode='rb', closefd=bool(closefd)))

        # read first line to determine tile; then reset the reader
        for tile,_,_ in TuplesDatasource._read_points(reader):
            break
        TuplesDatasource._set_tile(tile)
        reader.seek(0)
        self.gen = TuplesDatasource._read_points(reader)

        # fill in required interface
        self.envelope = tile_to_meters_Box2d(tile)
        self.data_type = mapnik.DataType.Vector
        super(TuplesDatasource, self).__init__(
            envelope = self.envelope
        )

    @staticmethod
    def _read_points(file):
        reader = csv.reader(file, delimiter="\t", strict=True)
        for rec in reader:
            if len(rec) != 3:
                inc_counter("read_points", "invalid_input")
                continue
            inc_counter("read_points", "point_count")
            log("TuplesDatasource._read_points() -> ('%s','%s','%s')" % (rec[0],float(rec[1]),float(rec[2])))
            yield (rec[0],float(rec[1]),float(rec[2]))

    @staticmethod
    def _points(src, expected_tile, bbox):
        for tile, mx, my in src:
            if not tile == expected_tile:
                raise DatasourceError("Unexpected tile! Was reading '%s', read '%s'" % (expected_tile, tile))
            p = Point(mx, my)
            if not bbox.contains(p):
                log("skipping point '%s'" % p)
                continue
            log("TuplesDatasource._points(_, '%s', '%s') -> '%s'" % (expected_tile, bbox, p))
            yield (p.wkb, {})

    def features(self, query):
        log("TuplesDatasource.features(%s)" % query.bbox)

        b = query.bbox
        bbox = box(b.minx, b.miny, b.maxx, b.maxy)
        return mapnik.PythonDatasource.wkb_features(
            keys = (),
            features = TuplesDatasource._points(self.gen, TuplesDatasource._get_tile(), bbox)
        )

# job code

def init_map(file):
    m = mapnik.Map(256, 256, _merc_srs)
    m.background_color = mapnik.Color('white')
    s = mapnik.Style()
    r = mapnik.Rule()
    r.symbols.append(mapnik.PointSymbolizer())
    s.rules.append(r)
    m.append_style('point_style', s)
    ds = mapnik.Python(factory='TuplesDatasource', fid=file.fileno())
    layer = mapnik.Layer('file', _merc_srs)
    layer.datasource = ds
    layer.styles.append('point_style')
    m.layers.append(layer)
    return m

def encode_image(im):
    s = base64.encodestring(im.tostring('png'))
    return s.replace('\n','')

if __name__=='__main__':
    map = init_map(stdin)
    map.zoom_all()
    im = mapnik.Image(256,256)
    mapnik.render(map,im)
    emit(TuplesDatasource._get_tile(), encode_image(im))
