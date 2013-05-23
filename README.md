# Tilebrute

Use [Apache Hadoop][hadoop] to generate map tiles.

> The author of this project is not responsible for your AWS usage.
> Don't come crying to me about your 1000$ AWS bill when you generate
> tiles for the whole country at 14 zoom levels. Consider this your
> notification and my indemnification.

[hadoop]: http://hadoop.apache.org

## Prerequisites

Before you can use Tilebrute, you'll need to install some
dependencies. Tilebrute uses GDAL, Shapely, and Mapnik, so you'll need
those libraries and their dependencies. Many of them are available on
a Mac via [Homebrew][homebrew]. For Ubuntu, the
[UbuntuGIS PPA][ubuntugis] may take you a long way. On other
platforms, the simplest path may be installing them from source.

You'll need:

- a modern Python
- GDAL
- Mapnik

Once you have these libraries installed, Pip should handle the python
side.

The whole dependency resolution process is automated via bootstrap
actions for EMR. Those files define the canonical dependency and
version details. Check out [`build_python.sh`][build_python] and
[`restore_python.sh`][restore_python].

[homebrew]: http://mxcl.github.io/homebrew/
[ubuntugis]: https://launchpad.net/~ubuntugis/+archive/ppa/
[build_python]: https://github.com/ndimiduk/tilebrute/blob/master/bin/build_python.sh
[restore_python]: https://github.com/ndimiduk/tilebrute/blob/master/bin/restore_python.sh

## Installation

With the prerequisites in place, the easiest way to install Tilebrute
is via pip's `git+https` interface.

    $ pip install git+https://github.com/ndimiduk/tilebrute.git

This is still a young project, so you're installing from master. At
some point it may become fancy enough for proper, tagged releases.

## Basic usage

The main entry point to Tilebrute is through the
[`tilebrute`][tilebrute] launch script that pip will install into your
python bin path. It can be used to run against a local Hadoop cluster
or to launch [Elastic MapReduce][emr] clusters. It's an extremely
basic [MrJob][mrjob] launch script, so that
[documentation][mrjob_docs] is more relevant than anything written
here.

Invocation of the script for an EMR job might look something like
this:

    $ MRJOB_CONF=mrjob.conf AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... \
      tilebrute --ec2-key-pair ... --ec2-key-pair-file ... \
      -r emr \
      --no-output --output-dir s3://bucket/output/tiles \
      s3://bucket/data/TIGER2010BLKPOPHU.csv/tabblock2010_53_pophu.csv

The key parameters here are:

- where to find the [`mrjob.conf`][conf] file (`MRJOB_CONF=`)
- AWS credentials (`AWS_ACCESS_KEY_ID=`, `AWS_SECRET_ACCESS_KEY=`)
- launch a job on EMR (`-r emr`), as opposed to a local cluster (`-r hadoop`)
- store output on S3 (`--no-output --output-dir s3://bucket/output/tiles`)
- specify the input (`tabblock2010_53_pophu.csv`)

[tilebrute]: https://github.com/ndimiduk/tilebrute/blob/master/bin/tilebrute
[emr]: http://aws.amazon.com/elasticmapreduce/
[mrjob]: https://github.com/Yelp/mrjob
[mrjob_docs]: http://pythonhosted.org/mrjob/
[conf]: https://github.com/ndimiduk/tilebrute/blob/master/mrjob.conf

## Preparing input data

Tilebrute expects input data to be in CSV format and the `epsg:4326`
projection. The [`prepare_input.sh`][prepare_input] script will mostly
take care of this for you. It's just a simple wrapper around `ogr2ogr`
with some defaults setup. Pass is `--help` for basic usage
information, or read the `ogr2ogr` documentation. Something like this
should suffice:

    $ 00_prepare_input.sh /vsizip/tabblock2010_53_pophu.zip | gzip -c > WA-epsg4326.csv.gz

[prepare_input]: https://github.com/ndimiduk/tilebrute/blob/master/bin/00_prepare_input.sh

## A simple preview

To get a feel for how Tilebrute works under the hood, the
[`simulated_hadoop.sh`][simulated_hadoop] script will connect the
components using UNIX pipes. It'll also sample the input data source
to make it easier to play. To override sampling, set the
`INPUT_LINE_LIMIT` environment variable. Assuming you've created the
`WA-epsg4326.csv.gz` input file, this command will render tiles for
the whole state using UNIX pipes.

    $ INPUT_LINE_LIMIT=200000 ./bin/10_simulated_hadoop.sh 

    real    302m54.667s
    user    306m6.092s
    sys     7m29.423s
      929859

That last line is the number of tiles rendered. The amount of time
taken will very based on how much data you give it and how many zoom
levels you choose to render.

[simulated_hadoop]: https://github.com/ndimiduk/tilebrute/blob/master/bin/10_simulated_hadoop.sh

## Configuration

All configuration is controlled by MrJob and resides in
[`mrjob.conf`][conf]. The examples are wired up, making assumptions
about S3 paths and cluster details. Each one is commented to some
degree or another. They should work as starting points for your own
uses. Be careful when uncommenting the configurations, especially the
ones at the bottom of the file; they'll use as many resources as your
default AWS account can provision. That's your responsibility, not
mine.

## License

Tilebrute is © 2013 Nick Dimiduk. Distributed under the [X11/MIT][mit]
License, same as GDAL. It is intended to give you permission to do
whatever you want with the Tilebrute source code: download, modify,
redistribute as you please, including building proprietary commercial
software, no permission from Mr. Dimiduk or anyone else is required.

Apache Hadoop is distributed under the
[Apache License Version 2.0][apache]. The spirit of that license is
similar.

[mit]: http://opensource.org/licenses/mit-license.php
[apache]: http://www.apache.org/licenses/LICENSE-2.0.html
