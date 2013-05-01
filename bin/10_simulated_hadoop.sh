#!/bin/bash
#
# 00_simulated_hadoop.sh run a demonstration of map-reduce, simulated
# with unix pipes.
#
# Don't run any map-reduce job, just demonstrate use of the underlying
# mapper and reducer scripts. Unix pipes and sort effectively emulate
# the data semantics provided by Hadoop. Read input from INPUT_FILES,
# limiting the input size by INPUT_LINE_LIMIT. Prints the output
# records and a count of their number to stdout.
#

BIN=$(dirname $0)
BIN=$(cd $BIN > /dev/null ; pwd)

source $BIN/01_sample_input.sh

PYTHON_DIR="src/main/python"

time \
  cat $INPUT_SAMPLED                                    `: read input records` \
  | python "${PYTHON_DIR}/sample_shapes.py" 2>/dev/null `: process them with the "mapper"` \
  | sort                                                `: sort the intermediate output` \
  | python "${PYTHON_DIR}/draw_tiles.py" 2>/dev/null    `: process the sorted records with the "reducer"` \
  | python "${PYTHON_DIR}/write_tiles.py"               `: write the output records with a simulated OutputFormat`

# count the output records
[ "$?" -eq "0" ] && find $OUTPUT_DIR | grep \\.png$ | wc -l `: finally, print and count the number of output records`
