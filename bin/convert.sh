#!/bin/bash -e

#
# Convert all the census files into CSV for tilebrute.
# Exercise to the reader: replace this script with a streaming job.
#

convert=/home/hadoop/TILE_BRUTE-virtualenv-x86_64/bin/00_prepare_input.sh

for x in $(hadoop fs -ls s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU/ | cut -d/ -f 2- | tail -n 51)
do
    x=$(basename $x)
    filename=${x%.*}
    echo "downloading s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU/$x"
    hadoop fs -get "s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU/$x" ./
    echo "converting $x to $filename.csv"
    $convert "/vsizip/$x" "$filename.csv"
    echo "putting s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU.csv/$filename.csv"
    hadoop fs -put "$filename.csv" s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU.csv/
    echo "compressing $filename.csv"
    gzip "$filename.csv"
    echo "putting s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU.csv.gz/$filename.csv.gz"
    hadoop fs -put "$filename.csv.gz" s3://tile-brute-us-west-2/data/TIGER2010BLKPOPHU.csv.gz/
    rm -f "$x" "$filename.csv.gz"
done
