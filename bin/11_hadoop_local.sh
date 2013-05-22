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

BIN=$(dirname $0)
BIN=$(cd $BIN > /dev/null ; pwd)

source $BIN/01_sample_input.sh

PYTHON=${PYTHON-$(which python)}

time \
  hadoop jar target/tilebrute-0.1.0-SNAPSHOT.jar `: launch hadoop` \
  -input $INPUT_SAMPLED                          `: reading these input records` \
  -output "$OUTPUT_DIR"                          `: generating output in this directory` \
  -mapper "$PYTHON -m tilebrute.sample_shapes"   `: using this mapper command` \
  -reducer "$PYTHON -m tilebrute.draw_tiles"     `: and this reducer command`

# count the output records
[ "$?" -eq "0" ] && wc -l "${OUTPUT_DIR}/part-00000"
