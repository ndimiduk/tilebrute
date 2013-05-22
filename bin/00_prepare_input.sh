#!/bin/bash -e
#
# Generate a CSV from an input shapefile, reprojecetd into EPSG:4326
# (WGS84 lat,lng coordinates). Geometries are preserved as pre-pended
# column "WKT".
#

if [[ $1 == "--help" ]] ; then
  echo "Usage: prepare_input.sh [input [output]]" >&2
  echo "Prepare a shapefile for use by tilebrute. Optional [input] is the path to an" >&2
  echo "ogr data source to be processed and output is an optional output path. In the" >&2
  echo "absence of either, stdin and stdout are used, respectively." >&2
  exit 1
fi

INPUT=${1-'/vsistdin/'}
OUTPUT=${2-'/vsistdout/'}

ogr2ogr                `: invoke gdal tool ogr2ogr` \
  -t_srs epsg:4326     `: reproject the data` \
  -f CSV               `: in CSV format` \
  $OUTPUT              `: producing output file` \
  $INPUT               `: from input file` \
  -lco GEOMETRY=AS_WKT `: including geometries as WKT`
