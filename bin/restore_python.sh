#!/bin/bash -e

bucketname="tile-brute-us-west-2"
ARCH=$(uname -m)

# this is important to ensure the virtualenv directory is restored in
# the right place.
cd ~

sudo apt-get -y install libtiff-dev libfreetype6-dev libxml2-dev libproj-dev libtool libcurl4-openssl-dev libgeos-dev

hadoop fs -get s3://$bucketname/emr_resources/dependencies/sqlite-autoconf-3070603-$ARCH.tar.gz ./
tar xzf sqlite-autoconf-3070603-$ARCH.tar.gz
cd sqlite-autoconf-3070603/
sudo make install
sudo ldconfig
cd ..

hadoop fs -get s3://$bucketname/emr_resources/dependencies/Python-2.7.3-$ARCH.tar.gz ./
tar xzf Python-2.7.3-$ARCH.tar.gz
cd Python-2.7.3/
sudo make install
sudo ldconfig
cd ..

hadoop fs -get s3://$bucketname/emr_resources/dependencies/icu4c-4_8_1_1-$ARCH.tar.gz ./
tar xzf icu4c-4_8_1_1-$ARCH.tar.gz
cd icu/source
sudo make install
sudo ldconfig
cd ../..

hadoop fs -get s3://$bucketname/emr_resources/dependencies/boost-1.52.0-$ARCH.tar.gz ./
tar xzf boost-1.52.0-$ARCH.tar.gz
cd boost_1_52_0/
sudo ./b2 install
sudo ldconfig
cd ..

hadoop fs -get s3://$bucketname/emr_resources/dependencies/gdal-1.9.1-$ARCH.tar.gz ./
tar xzf gdal-1.9.1-$ARCH.tar.gz
cd gdal-1.9.1
sudo make install
sudo ldconfig
cd ..

hadoop fs -get s3://$bucketname/emr_resources/dependencies/mapnik-2.1.0-$ARCH.tar.gz ./
tar xzf mapnik-2.1.0-$ARCH.tar.gz
cd mapnik-v2.1.0
sudo make install
sudo ldconfig
cd ..

# pull virtualenv
hadoop fs -get s3://$bucketname/emr_resources/dependencies/TILE_BRUTE-virtualenv-$ARCH.tar.gz ./
tar xzf TILE_BRUTE-virtualenv-$ARCH.tar.gz

# uncomment this line to always get the latest version of tilebrute
TILE_BRUTE-virtualenv-x86_64/bin/pip install -U git+https://github.com/ndimiduk/tile-brute.git

# confirm everything worked
./TILE_BRUTE-virtualenv-$ARCH/bin/python -c 'import mapnik ; import gdal ; import tilebrute'
