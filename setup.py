# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='velometro',
    version=version,
    description='Contains all of the Velometro specific documents and forms.',
    author='Velometro Mobility Inc',
    author_email='bcornwellmott@velometro.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
