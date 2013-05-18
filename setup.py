#
# based on ouline from http://learnpythonthehardway.org/book/ex46.html
#

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Create map tiles with Hadoop.',
    'author': 'Nick Dimiduk',
    'url': 'https://github.com/ndimiduk/tile-brute',
#    'download_url': 'Where to download it.',
    'author_email': 'printf(\'%s@%s.com\', \'ndimiduk\', \'gmail\')',
    'version': '0.1.0',
    'install_requires': ['GDAL==1.9.1', 'Shapely==1.2.17', 'mapnik2==2.1.0.5', 'mrjob==0.4', 'nose'],
    'package_dir': {'': 'src/main/python'},
    'packages' : ['tilebrute'],
    'scripts': ['bin/tilebrute', 'bin/00_prepare_input.sh', 'bin/01_sample_input.sh',
                'bin/10_simulated_hadoop.sh', 'bin/11_hadoop_local.sh',
                'bin/12_hadoop_local_outputfmt.sh'],
    'name': 'tilebrute'
}

setup(**config)
