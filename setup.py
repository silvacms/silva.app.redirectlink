# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0.1dev'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.app.redirectlink',
      version=version,
      description="Provides a link which does a permanent HTTP redirect to a moved Silva content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva app redirect permanent http',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.app.redirectlink',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Silva',
        'Products.SilvaMetadata',
        'five.grok',
        'grokcore.chameleon',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.smi',
        'silva.ui',
        'zope.component',
        'zope.container',
        'zope.interface',
        'zope.intid',
        'zope.publisher',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
