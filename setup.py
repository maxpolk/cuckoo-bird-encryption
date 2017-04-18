'''
Setup file to create a distribution.

Python 2 is not supported!  It is a different language, with a different
library, and different syntax.  No point diluting effort supporting
multiple languages when one is just fine.  Please don't port to Python 2,
instead, please try using Python 3.  Pushing for Python 2 is wasted effort
for you AND OTHERS, for no gain whatsoever.  Don't do that.

To create a source distribution, from this directory run the following which
creates a dist directory containing the distribution, and a
Cuckoo_Bird_Encryption.egg-info directory:

    python3 setup.py sdist --formats=gztar,zip

Instead of "sdist" above, see the list of other standard commands with:

    python3 setup.py --help-commands

To upload to PyPi, read more about the "register" and "upload" commands at:
    https://packaging.python.org/distributing/#uploading-your-project-to-pypi

This file is part of Cuckoo Bird Encryption, a secure messaging solution.
Copyright (C) 2017  Max Polk <maxpolk@gmail.com>
License located at http://www.gnu.org/licenses/gpl-3.0.html
'''
from setuptools import setup, find_packages

# Pick what to install
import sys
if sys.version_info[0] == 2:
    print ("Python 2 is not supported, please use Python 3")
    exit (1)

import os
import cuckoobird

setup (
    name=cuckoobird.software_name,
    version=cuckoobird.software_version,
    packages = ['cuckoobird', 'tests'],
    package_dir = {
        'cuckoobird': 'cuckoobird',
        'tests': 'tests'
    },
    scripts = [os.path.join ('bin', 'runtests'),
               os.path.join ('bin', 'snow')],
    install_requires = ['pymongo', 'tornado'],
    package_data = {
        # If any package contains *.txt, *.rst, or *.md files, include them:
        '': ['*.txt', '*.rst', '*.md'],
        # Include site.ini in teh cuckoobird package
        'cuckoobird': ['site.ini'],
    },
    # metadata for upload to PyPI
    author = "Max Polk",
    author_email = "maxpolk@gmail.com",
    description = cuckoobird.software_description,
    license = cuckoobird.software_abbreviation_license,
    keywords = "encryption",
    url = "http://cuckoobirdencryption.maxpolk.org/",   # project home page
    long_description = cuckoobird.software_long_description,
    # could also include long_description, download_url, classifiers, etc.
)
