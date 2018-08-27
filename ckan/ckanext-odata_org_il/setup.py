# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
import time

here = path.abspath(path.dirname(__file__))

if path.exists("VERSION.txt"):
    # this file can be written by CI tools (e.g. Travis)
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip().strip("v")
else:
    version = str(time.time())

setup(
    name='ckanext-odata_org_il',
    version=version,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    entry_points='''
        [ckan.plugins]
        odata_org_il=ckanext.odata_org_il.plugin:Odata_Org_IlPlugin
    ''',
)
