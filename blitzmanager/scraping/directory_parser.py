# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from abc import abstractmethod
from enum import Enum

from ..path import Path
import os
from ..logger import logger
from ..platform import PLATFORM

import re


class FilterTypes(Enum):
    E_DIRS = 1  # exclude_dirs
    E_FILES = 2  # exclude_files_containing
    I_FILES = 3  # include_files


def stringify_filter_type(f_type: FilterTypes):
    if f_type is FilterTypes.E_DIRS:
        return "exclude_dirs_"
    if f_type is FilterTypes.E_FILES:
        return "exclude_files_containing_"
    if f_type is FilterTypes.I_FILES:
        return "include_files_"

    return "unknown"


class DirectoryParserFilterOutput(object):
    def __init__(self):
        self.include_headers = []
        self.include_sources = []
        self.exclude_dirs = []
        self.exclude_files_containing = []


class DirectoryParserFilter(object):
    """
    Filter used by DirectoryHarvester to exclude/include directories or files
    depending on the current platform
    """

    def __init__(self):
        self.exclude_dirs_ = {"linux": [],
                              "windows": [],
                              "posix": [],
                              "any": []}

        self.exclude_files_containing_ = {"linux": [],
                                          "windows": [],
                                          "posix": [],
                                          "any": []}

        self.include_files_ = {"linux": {"HDRS": [],
                                         "SRCS": []},
                               "windows": {"HDRS": [],
                                           "SRCS": []},
                               "posix": {"HDRS": [],
                                         "SRCS": []},
                               "any": {"HDRS": [],
                                       "SRCS": []}}

    def set_linux(self, what: FilterTypes, content):
        getattr(self, f"{stringify_filter_type(what)}")["linux"] = content
        return self

    def set_windows(self, what: FilterTypes, content):
        getattr(self, f"{stringify_filter_type(what)}")["windows"] = content
        return self

    def set_any(self, what: FilterTypes, content):
        getattr(self, f"{stringify_filter_type(what)}")["any"] = content
        return self

    def set_posix(self, what: FilterTypes, content):
        getattr(self, f"{stringify_filter_type(what)}")["posix"] = content
        return self

    def posix(self, what: FilterTypes):
        return getattr(self, f"{stringify_filter_type(what)}")["posix"]

    def linux(self, what: FilterTypes):
        return getattr(self, f"{stringify_filter_type(what)}")["linux"]

    def windows(self, what: FilterTypes):
        return getattr(self, f"{stringify_filter_type(what)}")["windows"]

    def any(self, what: FilterTypes):
        return getattr(self, f"{stringify_filter_type(what)}")["any"]

    def __call__(self, *args, **kwargs):
        include_headers = []
        include_headers += self.any(FilterTypes.I_FILES)["HDRS"]

        include_sources = []
        include_sources += self.any(FilterTypes.I_FILES)["SRCS"]

        exclude_files_containing = []
        exclude_files_containing += self.any(FilterTypes.E_FILES)

        exclude_dirs = []
        exclude_dirs += self.any(FilterTypes.E_DIRS)

        if PLATFORM.is_posix():
            include_headers += self.posix(FilterTypes.I_FILES)["HDRS"]
            include_sources += self.posix(FilterTypes.I_FILES)["SRCS"]
            exclude_files_containing += self.posix(FilterTypes.E_FILES)
            exclude_dirs += self.posix(FilterTypes.E_DIRS)

        if PLATFORM.is_linux():
            include_headers += self.linux(FilterTypes.I_FILES)["HDRS"]
            include_sources += self.linux(FilterTypes.I_FILES)["SRCS"]
            exclude_files_containing += self.linux(FilterTypes.E_FILES)
            exclude_dirs += self.linux(FilterTypes.E_DIRS)

        if PLATFORM.is_windows():
            include_headers += self.windows(FilterTypes.I_FILES)["HDRS"]
            include_sources += self.windows(FilterTypes.I_FILES)["SRCS"]
            exclude_files_containing += self.windows(FilterTypes.E_FILES)
            exclude_dirs += self.windows(FilterTypes.E_DIRS)

        filter_output = DirectoryParserFilterOutput()
        filter_output.include_headers = include_headers
        filter_output.include_sources = include_sources
        filter_output.exclude_dirs = exclude_dirs
        filter_output.exclude_files_containing = exclude_files_containing

        return filter_output


class DirectoryParserCallback(object):
    """
    DirectoryParser observer
    """

    @abstractmethod
    def consume(self, subdirectory: str, file_name: str, relative_path: str, absolute_path: str):
        pass


class DirectoryParser(object):
    """
    Recursively iterate over a directory and extract all relevant
    files.
    """

    def __init__(self, input_dir: Path, callback: DirectoryParserCallback,
                 acceptable_extensions: str, filter_output: DirectoryParserFilterOutput,
                 exclude_files=None):

        if exclude_files is None:
            exclude_files = []

        assert input_dir.is_dir() and input_dir.is_abs(), f"The input path must be a directory and absolute : {input_dir}"

        self.__exclude_files_containing = filter_output.exclude_files_containing
        self.__exclude_files = exclude_files
        self.__dir = input_dir
        self.__callback = callback
        self.__exclude_dirs = filter_output.exclude_dirs
        self.__acceptable_extensions = re.compile(acceptable_extensions)
        self.__ignored_paths = []
        self.__ignored_directories = set()

    def ignored_paths(self):
        return list(sorted(self.__ignored_paths))

    def ignored_dirs(self):
        return list(sorted(list(self.__ignored_directories)))

    def parse(self):
        """

        :return:
        """
        self.__ignored_paths.clear()
        self.__ignored_directories.clear()

        source = self.__dir.path
        consumed_files = 0
        for root, subdirs, files in os.walk(source):

            relative_root_path = os.path.relpath(root, source)
            is_top_dir = len(relative_root_path.split(os.sep)) == 1
            if is_top_dir:
                if relative_root_path in self.__exclude_dirs:
                    self.__ignored_directories.add(root)
                    continue

            for file in files:
                input_file = os.path.join(root, file)
                assert Path(input_file).is_abs(), f"This path is not absolute :" \
                                                  f" {input_file} root :" \
                                                  f" {root} file : {file}" \
                                                  f" source : {source}"

                assert input_file not in self.__ignored_paths, f"Unexpected input file to be ignored again : {input_file}"
                self.__ignored_paths.append(input_file)
                if len(self.__acceptable_extensions.findall(input_file)) == 1:
                    file = os.path.relpath(os.path.join(root, file), source)
                    _continue = False
                    for maybe_escape in file.split(os.sep):
                        if maybe_escape in self.__exclude_dirs:
                            _continue = True
                            break

                    if _continue:
                        self.__ignored_directories.add(root)
                        continue

                    if any([sub in file.split(os.sep)[-1] for sub in self.__exclude_files_containing]):
                        continue

                    if any([sub == file.split(os.sep)[-1] for sub in self.__exclude_files]):
                        continue

                    subdirectory = relative_root_path.split(os.sep)[0]

                    base_relative_path = os.path.relpath(file, subdirectory)
                    self.__ignored_paths.remove(input_file)
                    assert Path(input_file).is_abs()
                    consumed_files += 1
                    self.__callback.consume(subdirectory, file.split(os.sep)[-1], base_relative_path, input_file)

        logger.info(f"Directory parser is done consumed_files = {consumed_files}")


class AbsolutePathsCallback(DirectoryParserCallback):
    def __init__(self):
        self.__absolute_paths = []

    def clear(self):
        self.__absolute_paths.clear()

    def absolute_paths(self):
        return sorted(self.__absolute_paths)

    def consume(self, subdirectory: str, file_name: str, relative_path: str, absolute_path: str):
        assert absolute_path not in self.__absolute_paths, "Fatal Error "
        self.__absolute_paths.append(absolute_path)


class AbsolutePathsCollector(object):
    def __init__(self, input_dir: Path,
                 acceptable_extensions: str, filter_output: DirectoryParserFilterOutput,
                 exclude_files=None):
        self.__callback = AbsolutePathsCallback()

        self.__parser = DirectoryParser(input_dir, self.__callback, acceptable_extensions, filter_output, exclude_files)

    def parser(self):
        self.__callback.clear()
        self.__parser.parse()
        return self

    def absolute_paths(self):
        return self.__callback.absolute_paths()


__all__ = ["DirectoryParser", "DirectoryParserCallback",
           "FilterTypes", "DirectoryParserFilterOutput", "AbsolutePathsCollector",
           "DirectoryParserFilter"]
