#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = '0.1.0'

setup(
    name='xoyuz',
    version=version,
    author='Eddy Ernesto del Valle Pino',
    author_email='xigmatron@gmail.com',
    description=(
        'Unifies and minifies static resources in production',
    ),
    long_description=read('README'),
    license='GPL',
    classifiers=[
        'Development Status :: 5 - Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: GPL',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='assets static files django css javascript',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django',
        'xoutil',
    ],
)
