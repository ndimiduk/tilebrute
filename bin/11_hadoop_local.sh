#!/bin/bash
#
# 01_hadoop_local.sh run the same demonstration of map-reduce
# streaming, using real Hadoop in local mode.
#
# Run a map-reduce job, but entirely in local mode. Read input from
# INPUT_FILES, limiting the input size by INPUT_LINE_LIMIT. This is
# done using a tmp file because Hadoop doesn't provide a simple
# sampling mechanism. Output records are written to OUTPUT_DIR using
# the standard Hadoop facilities. Print a count of their number to
# stdout.
#

INPUT_FILES=${INPUT_FILES-'WA-epsg4326.csv.gz'}
INPUT_LINE_LIMIT=${INPUT_LINE_LIMIT-'11'}
OUTPUT_DIR=${OUTPUT_DIR-'out'}

PYTHON_DIR="src/main/python"

# clean the output directory if it exits
[ -d "$OUTPUT_DIR" ] && rm -r "$OUTPUT_DIR"
# limit the input size to INPUT_LINE_LIMIT records
gzcat "$INPUT_FILES" | head -n "$INPUT_LINE_LIMIT" > /tmp/input.csv

hadoop jar target/tile-brute-0.1.0-SNAPSHOT.jar   `: launch hadoop` \
  -input /tmp/input.csv                           `: reading these input records` \
  -output "$OUTPUT_DIR"                           `: generating output in this directory` \
  -mapper "python ${PYTHON_DIR}/sample_shapes.py" `: using this mapper command` \
  -reducer "python ${PYTHON_DIR}/draw_tiles.py"   `: and this reducer command`

# count the output records
[ "$?" -eq "0" ] && wc -l "${OUTPUT_DIR}/part-00000"
