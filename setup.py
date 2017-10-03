#!/usr/bin/env python

from setuptools import setup

VERSION = "1.1.0.dev1"

setup(
    name="esanpy",
    version=VERSION,
    packages=['esanpy'],
    author="CodeLibs",
    author_email="dev@codelibs.org",
    license="Apache Software License",
    description=("Elasticsearch based Text Analyzer."),
    keywords="text analyzer",
    url="https://github.com/codelibs/esanpy",
    download_url='https://github.com/codelibs/esanpy/tarball/' + VERSION,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
        "console_scripts": [
            "esanpy=esanpy:main"
        ],
    },
)
