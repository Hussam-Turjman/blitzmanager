# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from .path import Path

import os


class TextFile(object):
    def __init__(self, path: Path):
        self.__path = path
        self.__f = None

    def open(self, how: str, encoding="utf8"):
        assert self.__f is None
        self.__f = open(self.__path.path, how, encoding=encoding)
        return self

    def close(self):
        assert self.__f is not None
        self.__f.close()
        self.__f = None
        return self

    def readall(self):
        return self.__f.read()

    def write(self, *args):
        for arg in args:
            assert type(arg) is str
            self.__f.write(arg)

        return self

    def writeline(self, content: list):
        for c in content:
            assert type(c) is str
            self.__f.write(c)
            self.__f.write("\n")

        return self


__all__ = ["TextFile"]
