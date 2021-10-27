# -*- coding: utf-8 -*-
from setuptools import setup
from os import path

directory = path.abspath(path.dirname(__file__))
with open(path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

packages = ['reader', 'reader.db', 'reader.pdf']

package_data = {'': ['*']}

install_requires = ['requests', 'lxml', 'beautifulsoup4==4.8.1', 'fpdf', 'colorama', ],

entry_points = {'console_scripts': ['rss_reader = reader.__main__:main', 'rss_reader.py = reader.__main__:main']}

setup_kwargs = {
    'name': 'rss_reader',
    'version': '1.5',
    'description': 'A simple CLI [RSS 2.0] reader',
    'long_description': long_description,
    'author': 'BotMan',
    'author_email': 'BotMan4@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9',
}

setup(**setup_kwargs)
