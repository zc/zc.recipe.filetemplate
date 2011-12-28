##############################################################################
#
# Copyright (c) 2011 Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""ZC Buildout recipe for creating templated files."""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


tests_require = [
    'zope.testing',
    ]
entry_points = """
[zc.buildout]
default = zc.recipe.filetemplate:FileTemplate
script = zc.recipe.filetemplate:ScriptTemplate
"""


setup(
    name='zc.recipe.filetemplate',
    version='0.1.0',
    author='Zvezdan Petkovic',
    author_email='zvezdan@zope.com',
    description=__doc__,
    long_description='\n\n'.join([
        read('README.txt'),
        '\n'.join([
            'Detailed Documentation',
            '**********************',
            ]),
        read('src', 'zc', 'recipe', 'filetemplate', 'README.txt'),
        read('CHANGES.txt'),
        ]),
    license='ZVSL 1.0',
    keywords=('zc.buildout buildout recipe file template'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License :: Zope Visible Source License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        ],
    # This is not public!
    url='http://svn.zope.com/zc.recipe.filetemplate/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zc', 'zc.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
        ],
    extras_require=dict(
        test=tests_require,
        ),
    tests_require=tests_require,
    test_suite='zc.recipe.filetemplate.tests.test_suite',
    entry_points=entry_points,
    )
