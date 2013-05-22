#!/bin/bash
#
# 02_hadoop_local_outputfmt.sh run the same demonstration of
# map-reduce streaming with Hadoop in local mode. Use a custom
# OutputFormat to generate PNG tiles.
#
# Run the same map-reduce job, again in local mode. This time, utilize
# the MapTileOutputFormat to generate map tiles as PNG files. Tiles
# are generated in the structure $OUTPUT_DIR/{z}/{x}/{y}.png. Print a
# count of their number to stdout.
#

BIN=$(dirname $0)
BIN=$(cd $BIN > /dev/null ; pwd)

source $BIN/01_sample_input.sh

PYTHON=${PYTHON-$(which python)}

time \
  hadoop jar target/tilebrute-0.1.0-SNAPSHOT.jar \
  -input $INPUT_SAMPLED \
  -output "$OUTPUT_DIR" \
  -mapper "$PYTHON -m tilebrute.sample_shapes" \
  -reducer "$PYTHON -m tilebrute.draw_tiles" \
  `: instruct Hadoop to use the custom OutputFormat` \
  -outputformat tilebrute.hadoop.mapred.MapTileOutputFormat

# count the output records
[ "$?" -eq "0" ] && find "$OUTPUT_DIR" | grep \\.png$ | wc -l
