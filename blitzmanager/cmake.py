# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from .command import Command
from .path import Path
from .logger import logger


class CMakeArguments(object):
    def __init__(self, install_path: Path, *extra_args, generator=None,
                 build_type="Release",
                 prefix_path=None, toolchain_path=None):
        self.__install_path = install_path
        self.__prefix_path = install_path.copy() if prefix_path is None else prefix_path
        self.__generator = generator
        self.__extra_args = extra_args
        self.__build_type = build_type
        self.__toolchain_path = toolchain_path

    @property
    def args(self):
        res = ["-DCMAKE_INSTALL_PREFIX={}".format(self.__install_path.path),
               "-DCMAKE_PREFIX_PATH={}".format(self.__prefix_path.path),
               "-DCMAKE_BUILD_TYPE={}".format(self.__build_type)]

        if self.__generator is not None:
            res.append("-G{}".format(self.__generator))
        if self.__toolchain_path is not None:
            res.append(f"-DCMAKE_TOOLCHAIN_FILE={self.__toolchain_path.path}")
        res += [str(a) for a in self.__extra_args]
        return [str(a) for a in res]

    def __str__(self):
        """

        :return:
        """
        return " ".join(self.args)


class CMakeBuilder(object):
    def __init__(self, cmake_args: CMakeArguments, input_path: Path, output_path: Path):
        """

        :param cmake_args:
        :param input_path:
        :param output_path:
        """
        self.__cmake_args = cmake_args.args
        self.__input_path = input_path
        self.__output_path = output_path

    def configure(self):
        """

        :return:
        """
        args = self.__cmake_args + [self.__input_path.path]
        Command(*args, program="cmake").execute(cwd=self.__output_path.path)
        return self

    def build(self, *args):
        """

        :return:
        """

        Command("--build", ".", "-j", "10", *args, program="cmake").execute(cwd=self.__output_path.path)

        return self

    def install(self, *args):
        """

        :return:
        """
        Command("--build", ".", "--target", "install", *args, program="cmake").execute(cwd=self.__output_path.path)
        return self

    def uninstall(self):
        """

        :return:
        """
        Command("--build", ".", "--target", "uninstall", program="cmake").execute(self.__output_path.path)

        return self


__all__ = ["CMakeArguments", "CMakeBuilder"]
