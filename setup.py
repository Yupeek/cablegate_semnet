#!/usr/env/python
# -*- coding: utf-8 -*-
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__="0.1"

__url__="https://github.com/elishowk/cablegate-db"
__longdescr__="Wikileaks CableGate Data Extraction Applications"
__license__="GNU General Public License v3"

__classifiers__= [
"Programming Language :: Python :: 2.6",
]

from setuptools import find_packages
from distutils.core import setup

setup (
    name = 'cablegate-db',
    packages = find_packages(),
    # Declare your packages' dependencies here, for eg:
    install_requires = ['pymongo','bson','beautifulsoup','nltk'],
    scripts = ['process_into_mongo.py'],
    version = __version__,
    url = __url__,
    long_description = __longdescr__,
    license = __license__,
    keywords = __keywords__,
    author = __author__,
    author_email = __author_email__,
    classifiers = __classifiers__,
    #test_suite = "unittest.TinasoftUnitTests",
    #dependency_links = DEPS,
)
