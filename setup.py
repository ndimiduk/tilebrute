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
    'install_requires': ['GDAL', 'mrjob', 'nose'],
    'package_dir': {'': 'src/main/python'},
    'packages' : ['tilebrute'],
    'scripts': [],
    'name': 'tilebrute'
}

setup(**config)
