# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blitzmanager",
    version="0.0.5",
    author="Hussam Turjman",
    author_email="hussam.turjman@gmail.com",
    description="Simple high level manager that uses package managers for C/C++ dependencies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hussam-Turjman/blitzmanager",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8.10',
    install_requires=["requests>=2.26.0"]
)
