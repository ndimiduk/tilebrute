#!/bin/bash -e

#
# elastic-mapreduce --create --alive --instance-group=master --instance-count=1 --instance-type=c1.xlarge --bid-price=0.450
#

# set a couple useful variables
bucketname="tile-brute-us-west-2"
ARCH=`uname -m`

# install build dependencies we can
sudo apt-get -y install libtiff-dev libfreetype6-dev libxml2-dev libproj-dev libtool libcurl4-openssl-dev libgeos-dev

# sqlite
wget http://www.sqlite.org/sqlite-autoconf-3070603.tar.gz
tar -vxf sqlite-autoconf-3070603.tar.gz
cd sqlite-autoconf-3070603
./configure
make
cd ..
tar -czf sqlite-autoconf-3070603-$ARCH.tar.gz sqlite-autoconf-3070603
hadoop fs -put sqlite-autoconf-3070603-$ARCH.tar.gz s3://${bucketname}/emr_resources/dependencies/
cd sqlite-autoconf-3070603
sudo make install
cd ..

# a modern python
wget http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tar.bz2
tar jfx Python-2.7.3.tar.bz2
cd Python-2.7.3
./configure ./configure --enable-shared --prefix=/usr
make -s
cd ..
tar -czf Python-2.7.3-$ARCH.tar.gz Python-2.7.3
hadoop fs -put Python-2.7.3-$ARCH.tar.gz s3://${bucketname}/emr_resources/dependencies/
cd Python-2.7.3
sudo make install
cd ..

# libicuuc
wget http://download.icu-project.org/files/icu4c/4.8.1.1/icu4c-4_8_1_1-src.tgz
tar xvzf icu4c-4_8_1_1-src.tgz
cd icu/source
chmod +x runConfigureICU configure install-sh
./runConfigureICU Linux
make
make check
cd ../..
tar -czf icu4c.tar.gz icu
hadoop fs -put icu4c.tar.gz s3://${bucketname}/emr_resources/dependencies/
cd icu/source
sudo make install
cd ../..

# boost 1.52.0
wget http://downloads.sourceforge.net/project/boost/boost/1.52.0/boost_1_52_0.tar.bz2
tar xjf boost_1_52_0.tar.bz2
cd boost_1_52_0
./bootstrap.sh
./b2
cd ..
tar -czf boost-1.52.0.tar.gz boost_1_52_0
hadoop fs -put boost-1.52.0.tar.gz s3://${bucketname}/emr_resources/dependencies/
cd boost_1_52_0
sudo ./b2 install
cd ..

# gdal
wget http://download.osgeo.org/gdal/gdal-1.9.1.tar.gz
tar xvzf gdal-1.9.1.tar.gz
cd gdal-1.9.1
./configure --with-python --with-geos
make
cd ..
tar -czf gdal-1.9.1-$ARCH.tar.gz gdal-1.9.1
hadoop fs -put gdal-1.9.1-$ARCH.tar.gz s3://${bucketname}/emr_resources/dependencies/
cd gdal-1.9.1
sudo make install
sudo ldconfig

# mapnik
wget https://github.com/downloads/mapnik/mapnik/mapnik-v2.1.0.tar.bz2
tar xjf mapnik-v2.1.0.tar.bz2
cd mapnik-v2.1.0
./configure
make
cd ..
tar -czf mapnik-2.1.0-$ARCH.tar.gz mapnik-v2.1.0
hadoop fs -put mapnik-2.1.0-$ARCH.tar.gz s3://${bucketname}/emr_resources/dependencies/
cd mapnik-v2.1.0
sudo make install
sudo ldconfig
cd ..

###
# Finished with C/++. Now for Python side
#

# install virtualenv from source
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.1.tar.gz
tar xvfz virtualenv-1.9.1.tar.gz
cd virtualenv-1.9.1
sudo python setup.py install
cd ..

# move into the virtualenv
virtualenv --distribute TILE_BRUTE-virtualenv-$ARCH
source TILE_BRUTE-virtualenv-$ARCH/bin/activate

# install tilebrute and dependencies
pip install -U git+https://github.com/ndimiduk/tile-brute.git

# confirm everything worked
./TILE_BRUTE-virtualenv-$ARCH/bin/python -c 'import mapnik ; import gdal ; import tilebrute'

tar -czf TILE_BRUTE-virtualenv-$ARCH.tar.gz TILE_BRUTE-virtualenv-$ARCH
hadoop fs -put TILE_BRUTE-virtualenv-$ARCH.tar.gz s3://${bucketname}/emr_resources/dependencies/
