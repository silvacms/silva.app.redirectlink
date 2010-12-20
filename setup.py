# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='silva.app.redirectlink',
      version=version,
      description="A link which does a permanent HTTP redirect to a Silva Object",
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
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Products.Silva',
          'five.grok',
          'setuptools',
          'silva.core.conf',
          'silva.core.interfaces',
          'silva.core.views',
          'zope.component',
          'zope.interface',
          'zope.testing',
          ],
      )
