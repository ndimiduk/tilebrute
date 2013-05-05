#!/bin/bash
#
# 01_sample_input.sh handles parsing down input file size for local
# execution. Code shared by 10_*.
#

export INPUT_FILES=${INPUT_FILES-'WA-epsg4326.csv.gz'}
export INPUT_LINE_LIMIT=${INPUT_LINE_LIMIT-'11'}
export INPUT_SAMPLED=${INPUT_SAMPLED-'/tmp/input.csv'}
export OUTPUT_DIR=${WRITE_TILES_OUT-'out'}

CAT="gunzip -c"

# clean the output directory if it exits
[ -d "$OUTPUT_DIR" ] && rm -r "$OUTPUT_DIR"
# limit the input size to INPUT_LINE_LIMIT records
$CAT "$INPUT_FILES" | head -n "$INPUT_LINE_LIMIT" > $INPUT_SAMPLED
