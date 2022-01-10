# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.
import json
from typing import List

from .path import Path
from .managers import SupportedManagers, ManagerInitializer, PackageManager
from .arguments_parser import ArgumentsParser
from .dependency_builder import DependencyBuilder
from .flag_observer import FlagObserver
from .cmake import CMakeArguments
from .logger import logger, set_global_verbose
from .template_parser import TemplateGenerator
from .templates_path_loader import TEMPLATES_PATH
import atexit
import sys


class BlitzManager(object):
    __arguments_parser: ArgumentsParser
    __manager_initializer: ManagerInitializer
    __package_manager: PackageManager
    __dependency_builder: DependencyBuilder

    def __init__(self):
        atexit.register(self.__exit_handler)
        self.__arguments_parser = ArgumentsParser(description="BlitzManager is a tool for managing C/C++ dependencies.")
        self.__flags = {}
        self.__manager_initializer = None
        self.__package_manager = None

        self.__dependencies = {}
        self.list_managers = False
        self.list_templates = False
        self.verbose = 5
        self.version = False
        self.ct = None
        self.version_info = "0.0.0"
        self.clear_flags()

    @property
    def dependencies(self):
        return self.__dependencies

    @property
    def manager_install_path(self):
        return self.__package_manager.install_path()

    def __exit_handler(self):
        """

        :return:
        """

    def initialize(self, manager_output_path: Path,
                   build_output_path: Path,
                   install_output_path: Path,
                   package_manager: SupportedManagers,
                   source_root_path: Path = None):
        """

        :param source_root_path: Optional source root path to avoid giving the input path, when building from source code.
        :param manager_output_path: Path for the blitz-manager output. (downloaded zip files and to build external tools)
        :param build_output_path: Path for building external dependencies you specify.
        :param install_output_path: Path for installing the external dependencies.
        :param package_manager: The C/C++ package manger you wish to use.
        :return:
        """
        if source_root_path is not None:
            if not (source_root_path.is_dir() or source_root_path.is_abs()):
                raise RuntimeError(f"Source root path: {source_root_path} is not a directory.")
        else:
            source_root_path = Path.cwd()
        if manager_output_path.is_file():
            raise RuntimeError(f"Manager output path is a file : {manager_output_path}")
        if build_output_path.is_file():
            raise RuntimeError(f"Build output path is a file : {build_output_path}")
        if install_output_path.is_file():
            raise RuntimeError(f"Install path is a file : {install_output_path}")
        manager_output_path.make(directory=True, ignore_errors=True)
        build_output_path.make(directory=True, ignore_errors=True)
        install_output_path.make(directory=True, ignore_errors=True)

        logger.info(f"Manager output path : {manager_output_path}", verbose=10)
        logger.info(f"Build output path : {build_output_path}", verbose=10)
        logger.info(f"Install output path : {install_output_path}", verbose=10)
        logger.info(f"Source root directory : {source_root_path}", verbose=10)
        self.__manager_output_path = manager_output_path
        self.__build_output_path = build_output_path
        self.__install_output_path = install_output_path
        self.__package_manager_type = package_manager
        self.__source_root_path = source_root_path
        self.__dependency_builder = DependencyBuilder(output_dir=self.__build_output_path)
        return self

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
        self.add_flag("--list_templates", default=False, help="List available CMake templates.",
                      action="store_true")
        self.add_flag("--version",
                      help="Display version information",
                      default=False,
                      action="store_true")

        self.add_flag("--ct", nargs=3,
                      help="Create CMake project template. Usage :  [template_name] [path to config.json] [output_dir]",
                      required=False,
                      default=None)

    def __list_mangers(self):
        """

        :return:
        """
        print("Available C/C++ package managers : ")
        print()
        for i, m in enumerate(ManagerInitializer.supported_managers()):
            print(f"Manager [{i}] : {m}")
        print()
        print()
        sys.exit(0)

    def __call_default_flags(self):
        """

        :return:
        """
        set_global_verbose(self.verbose)

        if self.list_managers:
            self.__list_mangers()
        if self.list_templates:
            TemplateGenerator.list_available_templates(TEMPLATES_PATH)
            sys.exit(0)
        if self.version:
            print(f"""
            BlitzManager version {self.version_info}

            See the LICENSE file for license information.
            """)
            sys.exit(0)
        if self.ct is not None:
            template_name = self.ct[0]
            with open(self.ct[1], "r") as f:
                config = json.load(f)
                f.close()
            output_dir = Path(self.ct[2])
            self.create_template(template_name, config, output_dir)
            sys.exit(0)

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

    def add_flags(self, flags: dict):
        """

        :param flags: dictionary of flags as keys and options as value.
        :return:
        """
        for flag in flags.keys():
            if not isinstance(flags[flag], dict):
                raise RuntimeError("Flag value must also be a dictionary")
            self.add_flag(flag, **flags[flag])
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

    def create_template(self, template_name: str, config: dict, output_dir: Path):
        """

        :param template_name:
        :param config: meta information about the template
        :param output_dir:
        :return:
        """
        if output_dir.is_file():
            raise RuntimeError("Output directory is a file.")
        template_path = TEMPLATES_PATH.copy().join(template_name)
        build_dir = output_dir.copy()

        config["template_path"] = template_path
        config["build_dir"] = build_dir
        generator = TemplateGenerator(config)
        generator.generate()
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

        self.__arguments_parser.parse(namespace=self)
        self.__call_default_flags()
        return self

    def initialize_managers(self, override=False):
        """
        Initialize C/C++ package managers.
        :return:
        """
        if self.__package_manager_type is SupportedManagers.NONE:
            logger.info("Skipping initialization step for the package managers.", verbose=3)
            return self
        self.__manager_initializer = ManagerInitializer(output_path=self.__manager_output_path)
        try:
            self.__manager_initializer.download(override=override).build()
        except KeyboardInterrupt as e:
            logger.error("KeyboardInterrupt. You may need to remove the output directory.")
        try:
            self.__package_manager = self.__manager_initializer.managers[self.__package_manager_type.value]
        except IndexError:
            logger.error(
                "IndexError. You need to delete the output directory to solve this problem."
                " This happens if previous download didn't complete")
        return self

    def clear_dependencies(self):
        """

        :return:
        """
        self.__dependencies.clear()
        return self

    def build_dependencies(self):
        """
        Build all previously added dependencies.
        :return:
        """
        for dep in self.__dependencies.keys():
            logger.info(f"Started building : [{dep}] ..", verbose=3)
            input_dir, cmake_args, delete_cache = self.__dependencies[dep]
            if input_dir is None and cmake_args is None:
                if self.__package_manager_type is SupportedManagers.NONE:
                    logger.info(f"Skipping dependency [{dep}]", verbose=3)
                    continue
                self.__dependency_builder.build_via_package_manager(dep, self.__package_manager)
                continue
            self.__dependency_builder.build_from_source(dep, input_dir, cmake_args, delete_cache=delete_cache)
        return self

    def build_from_source(self, dependency: str, *args, input_dir: Path = None, **kwargs, ):
        """

        :param dependency: Name of the dependency.
        :param input_dir: Absolute path of the source code, where the CMakeLists.txt reside.
        :param kwargs: Arguments to pass to CMakeArguments.
        :param args: Arguments to pass to cmake directly.
        :return:
        """
        if input_dir is None:
            if self.__source_root_path is None:
                raise RuntimeError(
                    f"Input directory and source root path are both not set. Unable to locate [{dependency}]")
            input_dir = Path(self.__source_root_path.path, dependency)
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
        if self.__package_manager_type == SupportedManagers.NONE:
            return self
        for dependency in dependencies:
            self.__dependencies[dependency] = (None, None, None)
        return self
