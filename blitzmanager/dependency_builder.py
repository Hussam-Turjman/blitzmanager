# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from .path import Path
from .cmake import CMakeArguments, CMakeBuilder
from .managers import PackageManager


class DependencyBuilder(object):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        assert output_dir.is_dir()

    def build_from_source(self, dependency: str, input_dir: Path, cmake_args: CMakeArguments, delete_cache=False):
        """

        :param delete_cache:
        :param dependency:
        :param input_dir:
        :param cmake_args:
        :return:
        """
        output_path = Path(self.output_dir.path, f"{dependency}_build")
        output_path.make(directory=True, ignore_errors=True)
        if delete_cache:
            Path(output_path.path, "CMakeCache.txt").remove(ignore_errors=True)
        builder = CMakeBuilder(cmake_args, input_dir, output_path)
        builder.configure().build("--config", "Release").install("--config", "Release")
        return self

    def build_via_package_manager(self, dependency: str, manager: PackageManager):
        """

        :param dependency:
        :param manager:
        :return:
        """
        output_path = Path(self.output_dir.path, dependency)
        manager.build(dependency).install(dependency, output_path)
        return self


__all__ = ["DependencyBuilder"]
