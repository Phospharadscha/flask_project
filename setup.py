"""Describes the project and the files that belong to it. 
    Can be used to install the package to somewhere with pip, as it tells python what files to download
"""

from setuptools import find_packages, setup

setup(
    name='toolbox',
    version='1.0.0',
    packages=find_packages(), 
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)