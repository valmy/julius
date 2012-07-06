try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'T. Budiman',
    'url': 'https://github.com/valmy/python-skeleton',
    'download_url': 'https://github.com/valmy/python-skeleton/zipball/master',
    'author_email': 'tbudiman@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'projectname'
}

setup(**config)
