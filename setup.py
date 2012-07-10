try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Julius Swiss Pairing System',
    'author': 'T. Budiman',
    'url': 'https://github.com/valmy/julius',
    'download_url': 'https://github.com/valmy/julius/zipball/master',
    'author_email': 'tbudiman@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['julius'],
    'scripts': [],
    'name': 'julius'
}

setup(**config)
