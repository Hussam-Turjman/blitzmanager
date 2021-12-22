#!/bin/sh

set -e                            # exit on errors

rm -rf dist
rm -rf blitzmanager.egg-info
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade build
python3 -m build
# python3 -m pip install --upgrade twine
python3 -m twine upload  --repository pypi dist/*
