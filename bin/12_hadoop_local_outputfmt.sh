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

INPUT_FILES=${INPUT_FILES-'WA-epsg4326.csv.gz'}
INPUT_LINE_LIMIT=${INPUT_LINE_LIMIT-'11'}
OUTPUT_DIR=${OUTPUT_DIR-'out'}

PYTHON_DIR="src/main/python"

# clean the output directory if it exits
[ -d "$OUTPUT_DIR" ] && rm -r "$OUTPUT_DIR"
# limit the input size to INPUT_LINE_LIMIT records
gzcat "$INPUT_FILES" | head -n "$INPUT_LINE_LIMIT" > /tmp/input.csv

time \
  hadoop jar target/tile-brute-0.1.0-SNAPSHOT.jar \
  -input /tmp/input.csv \
  -output "$OUTPUT_DIR" \
  -mapper "python ${PYTHON_DIR}/sample_shapes.py" \
  -reducer "python ${PYTHON_DIR}/draw_tiles.py" \
  `: instruct Hadoop to use the custom OutputFormat` \
  -outputformat tilebrute.hadoop.mapred.MapTileOutputFormat

# count the output records
[ "$?" -eq "0" ] && find "$OUTPUT_DIR" | grep \\.png$ | wc -l
