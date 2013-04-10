#!/bin/sh
#
# Generate a CSV from an input shapefile, reprojecetd into EPSG:4326
# (WGS84 lat,lng coordinates). Geometries are preserved as pre-pended
# column "WKT".
#

ogr2ogr                `: invoke gdal tool ogr2ogr` \
  -progress            `: print progress as we go` \
  -t_srs epsg:4326     `: reproject the data` \
  -f CSV               `: in CSV format` \
  WA-epsg4326.csv      `: producing output file` \
                       `: from input file` \
  ~/Downloads/TIGER2010BLKPOPHU-1/tabblock2010_53_pophu/tabblock2010_53_pophu.shp \
  -lco GEOMETRY=AS_WKT `: including geometries as WKT`
