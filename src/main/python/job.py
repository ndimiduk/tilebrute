#!/usr/bin/env python
#
# A MRJob definition for TileBrute. This is how we'll normalize
# launching the job locally in pseudo-distributed mode and on the
# cloud.
#
# {Inline,Local}MRJobRunners don't actually work, for reasons I don't
# understand.
#
# To use with HadoopJobRunner:
# $ HADOOP_HOME=/path/to/hadoop/install \
#   python ./src/main/python/job.py -r hadoop
#   /path/to/input.csv \
#   --no-output -o out # <- these are important because otherwise
#                      #    MRJob will attempt to print your pngs
#                      #    to stdout o.O
#
# To use with EMRJobRunner:
# ???
#

from mrjob.job import MRJob
from mrjob.util import bash_wrap

class TileBrute(MRJob):

    # use this in combination with prepare_shapefiles
#    HADOOP_INPUT_FORMAT = 'org.apache.hadoop.mapred.lib.NLineInputFormat'

    # for generating Google TileID structure, ie, {z}/{x}/{y}.png
    HADOOP_OUTPUT_FORMAT = 'tilebrute.hadoop.mapred.MapTileOutputFormat'

    def mapper_cmd(self):
        return bash_wrap('python ${PYTHON_DIR}/sample_shapes.py')

    def reducer_cmd(self):
        return bash_wrap('python ${PYTHON_DIR}/draw_tiles.py')

if __name__ == '__main__':
    TileBrute.run()
