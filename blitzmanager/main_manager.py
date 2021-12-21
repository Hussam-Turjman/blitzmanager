# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.
from typing import List

from .path import Path
from .managers import SupportedManagers, ManagerInitializer, PackageManager
from .arguments_parser import ArgumentsParser
from .dependency_builder import DependencyBuilder
from .flag_observer import FlagObserver
from .cmake import CMakeArguments
from .logger import logger
import sys


class BlitzManager(object):
    __arguments_parser: ArgumentsParser
    __manager_initializer: ManagerInitializer
    __package_manager: PackageManager
    __dependency_builder: DependencyBuilder

    def __init__(self, manager_output_path: Path,
                 build_output_path: Path,
                 install_output_path: Path,
                 package_manager: SupportedManagers):
        """

        :param manager_output_path: Path for the blitz-manager output. (downloaded zip files and to build external tools)
        :param build_output_path: Path for building external dependencies you specify.
        :param install_output_path: Path for installing the external dependencies.
        :param package_manager: The C/C++ package manger you wish to use.
        """
        if manager_output_path.is_file():
            raise RuntimeError(f"Manager output path is a file : {manager_output_path}")
        if build_output_path.is_file():
            raise RuntimeError(f"Build output path is a file : {build_output_path}")
        if install_output_path.is_file():
            raise RuntimeError(f"Install path is a file : {install_output_path}")
        manager_output_path.make(directory=True, ignore_errors=True)
        build_output_path.make(directory=True, ignore_errors=True)
        install_output_path.make(directory=True, ignore_errors=True)

        logger.info(f"Manager output path : {manager_output_path}")
        logger.info(f"Build output path : {build_output_path}")
        logger.info(f"Install output path : {install_output_path}")

        self.__manager_output_path = manager_output_path
        self.__build_output_path = build_output_path
        self.__install_output_path = install_output_path
        self.__package_manager_type = package_manager
        self.__arguments_parser = ArgumentsParser(description="BlitzManager is a tool for manging C/C++ dependencies.")
        self.__flags = {}
        self.__manager_initializer = None
        self.__package_manager = None
        self.__dependency_builder = DependencyBuilder(output_dir=self.__build_output_path)
        self.__dependencies = {}
        self.list_managers = False
        self.verbose = 5
        self.clear_flags()

    def __add_default_flags(self):
        """

        :return:
        """
        self.add_flag("--verbose",
                      default=5,
                      help="Logging verbosity",
                      required=False,
                      type=int)
        self.add_flag("--list_managers", default=False,
                      help="List of supported C/C++ package managers.",
                      action="store_true")

    def __list_mangers(self):
        """

        :return:
        """
        for i, m in enumerate(ManagerInitializer.supported_managers()):
            logger.info(f"Manager [{i}] : {m}")
        sys.exit(0)

    def __call_default_flags(self):
        """

        :return:
        """
        if self.list_managers:
            self.__list_mangers()

    @property
    def arguments_parser(self) -> ArgumentsParser:
        """
        ArgumentsParser is for adding custom flags to the blitz-manager.
        :return:
        """
        return self.__arguments_parser

    def get_flag_value(self, flag: str) -> object:
        """
        Get the value of a previously specified flag.
        :param flag:
        :return:
        """
        return getattr(self, flag)

    def __getitem__(self, flag):
        """
        Same as get_flag_value.
        :param flag:
        :return:
        """
        return self.get_flag_value(flag)

    def add_flag(self, flag: str, *args, **kwargs):
        """

        :param flag:
        :param args:
        :param kwargs:
        :return:
        """

        self.__arguments_parser.add_flag(flag, *args, **kwargs)
        return self

    def add_flag_observer(self, flag: str, observer: FlagObserver):
        """

        :param flag: Flag name without any switches. For example "port".
        :param observer: Observer to notify when the flag is set.
        :return:
        """
        if flag not in self.__arguments_parser.flags:
            raise RuntimeError(f"Flag {flag} is not set.")
        self.__flags[flag] = observer
        return self

    def notify_flag_observers(self):
        """
        Notify all flags observers.
        :return:
        """
        for flag in self.__flags.keys():
            self.__flags[flag].flag_set(flag, getattr(self, flag))
        return self

    def clear_flags(self):
        """
        Clear all flags and their observers.
        :return:
        """
        self.__flags.clear()
        for flag in self.__arguments_parser.flags:
            delattr(self, flag)
        self.__arguments_parser = ArgumentsParser(description="BlitzManager is a tool for manging C/C++ dependencies.")
        self.__arguments_parser.flags.clear()
        self.__add_default_flags()
        return self

    def parse_arguments(self):
        """
        Parse command line arguments.
        :return:
        """
        self.clear_flags()
        self.__arguments_parser.parse(namespace=self)
        self.__call_default_flags()
        return self

    def initialize_managers(self, override=False):
        """
        Initialize C/C++ package managers.
        :return:
        """
        if self.__package_manager_type is SupportedManagers.NONE:
            logger.info("Skipping initialization step for the package managers.")
            return self
        self.__manager_initializer = ManagerInitializer(output_path=self.__manager_output_path)
        self.__manager_initializer.download(override=override).build()
        self.__package_manager = self.__manager_initializer.managers[self.__package_manager_type.value]
        return self

    def clear_dependencies(self):
        """

        :return:
        """
        self.__dependencies.clear()
        return self

    def build_dependencies(self):
        """
        Build all previously add dependencies.
        :return:
        """
        for dep in self.__dependencies.keys():
            logger.info(f"Started building : [{dep}] ..")
            input_dir, cmake_args, delete_cache = self.__dependencies[dep]
            if input_dir is None and cmake_args is None:
                if self.__package_manager_type is SupportedManagers.NONE:
                    logger.info(f"Skipping dependency [{dep}]")
                    continue
                self.__dependency_builder.build_via_package_manager(dep, self.__package_manager)
                continue
            self.__dependency_builder.build_from_source(dep, input_dir, cmake_args, delete_cache=delete_cache)
        return self

    def build_from_source(self, dependency: str, input_dir: Path, *args, **kwargs):
        """

        :param dependency: Name of the dependency.
        :param input_dir: Absolute path of the source code, where the CMakeLists.txt reside.
        :param kwargs: Arguments to pass to CMakeArguments.
        :param args: Arguments to pass to cmake directly.
        :return:
        """
        install_path = kwargs.pop("install_path", self.__install_output_path)
        generator = kwargs.pop("generator", None)
        build_type = kwargs.pop("build_type", "Release")
        prefix_path = kwargs.pop("prefix_path", None)
        add_toolchain_path = kwargs.pop("add_toolchain", True)
        delete_cache = kwargs.pop("delete_cache", False)
        toolchain_path = None
        if add_toolchain_path:
            toolchain_path = self.__package_manager.toolchain_path().copy() if self.__package_manager_type \
                                                                               is not SupportedManagers.NONE else None
        if not input_dir.is_dir():
            raise RuntimeError(f"The dependency [{dependency}] path : {input_dir} is not a directory")
        self.__dependencies[dependency] = (input_dir, CMakeArguments(install_path.copy(),
                                                                     *args,
                                                                     generator=generator,
                                                                     build_type=build_type,
                                                                     prefix_path=prefix_path,
                                                                     toolchain_path=toolchain_path
                                                                     ), delete_cache)
        return self

    def build_via_package_manager(self, dependencies: List[str]):
        """
        Add list of dependencies to build via the package manager.
        :param dependencies:
        :return:
        """
        for dependency in dependencies:
            self.__dependencies[dependency] = (None, None, None)
        return self
