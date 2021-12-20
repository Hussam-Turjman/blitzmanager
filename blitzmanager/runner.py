# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.
from typing import List

from .arguments_parser import ArgumentsParser
from .managers import ManagerInitializer, PackageManager
from .path import Path
from .flag_observer import FlagObserver
from .dependency_builder import DependencyBuilder


class Runner(object):
    initializer: ManagerInitializer

    def __init__(self, parser: ArgumentsParser):
        """

        :param parser:
        """
        self.parser = parser
        self.flags = {}
        self.output_dir = Path("")
        self.__builder = None
        self.initializer = None

    def add_flag_observer(self, flag: str, observer: FlagObserver):
        """

        :param flag:
        :param observer:
        :return:
        """
        self.flags[flag] = observer

    def notify_flag_observers(self):
        """

        :return:
        """
        for flag in self.flags.keys():
            self.flags[flag].flag_set(flag, getattr(self, flag))

    def clear_flags(self):
        """

        :return:
        """
        self.parser.flags.clear()
        self.flags.clear()

    def run(self, package_manager_output_path: Path):
        """

        :param package_manager_output_path:
        :return:
        """
        assert not package_manager_output_path.is_file()
        package_manager_output_path.make(directory=True, ignore_errors=True)

        self.parser.parse(namespace=self)

        self.initializer = ManagerInitializer(output_path=package_manager_output_path)
        self.initializer.download().build()
        self.output_dir = package_manager_output_path.copy()
        self.__builder = DependencyBuilder(self.output_dir)

    def builder(self) -> DependencyBuilder:
        """

        :return:
        """
        assert self.output_dir.is_dir()
        return self.__builder

    def managers(self) -> List[PackageManager]:
        """

        :return:
        """
        return self.initializer.managers


__all__ = ["Runner"]
