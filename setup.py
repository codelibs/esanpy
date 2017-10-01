#!/usr/bin/env python

from setuptools import setup

setup(
    name="esanpy",
    version="0.0.1",
    packages=['esanpy'],
    author="CodeLibs",
    author_email="dev@codelibs.org",
    license="Apache Software License",
    description=("Elasticsearch based Text Analyzer."),
    keywords="text analyzer",
    url="https://github.com/codelibs/esanpy",
    download_url='https://github.com/codelibs/esanpy/tarball/0.0.1',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
        "console_scripts": [
            "esanpy=esanpy:main"
        ],
    },
)
