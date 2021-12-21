# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import os

from .cmake_creator import CMakeCreator
from .DirectoryParser import DirectoryParserCallback, DirectoryParser, DirectoryParserFilter
from ..text_file import TextFile
from ..path import Path


class ParserCallback(DirectoryParserCallback):
    """
    DirectoryParser observer
    """

    def __init__(self,ignore_sub_directories=False):
        self.__ignore_sub_directories = ignore_sub_directories
        self.__sources_map = []
        self.__headers_map = []
        self.__absolute_paths = []

    def reset(self):
        self.__headers_map.clear()
        self.__sources_map.clear()
        self.__absolute_paths.clear()

    def sources(self):
        return self.__sources_map

    def headers(self):
        return self.__headers_map

    def absolute_paths(self):
        return self.__absolute_paths

    def consume(self, subdirectory: str, file_name: str, relative_path: str, absolute_path: str):
        """

        :param subdirectory:
        :param file_name:
        :param relative_path:
        :param absolute_path:
        :return:
        """
        subdirectory = subdirectory.replace(os.sep, "/")
        relative_path = relative_path.replace(os.sep, "/")

        is_header = file_name.endswith(".h")

        if self.__ignore_sub_directories and subdirectory != ".":
            return

        if subdirectory != ".":
            relative_path = f"{subdirectory}/" + relative_path

        if is_header:
            self.__headers_map.append(relative_path)
        else:
            self.__sources_map.append(relative_path)

        self.__absolute_paths.append(absolute_path)


class DirectoryHarvester(object):
    """
    As the name says, this class is for harvesting a directory recursively
    and extracting all relevant files to create a CMakeLists.txt script.

    """

    def __init__(self, libname: str, path: Path,
                 acceptable_extensions: str,
                 directory_filter: DirectoryParserFilter,
                 deps: list,
                 defines: list,ignore_sub_directories=False,
                 object_lib=False):

        self.__deps = deps
        self.__defines = defines
        self.__harvester_filter = directory_filter
        self.__libname = libname
        self.__cmake_creator = CMakeCreator(libname,object_lib=object_lib)
        self.__callback = ParserCallback(ignore_sub_directories)
        self.__path = path
        self.__acceptable_extensions = acceptable_extensions
        self.__directory_parser = None

        assert self.__path.is_dir()

    def parse(self):
        """

        :return:
        """
        self.__cmake_creator.reset()
        self.__callback.reset()

        filter_output = self.__harvester_filter()

        self.__cmake_creator.append_sources(filter_output.include_sources)
        self.__cmake_creator.append_headers(filter_output.include_headers)

        self.__directory_parser = DirectoryParser(self.__path, self.__callback,
                                                  filter_output=filter_output,
                                                  acceptable_extensions=self.__acceptable_extensions)

        self.__directory_parser.parse()

        self.__cmake_creator.append_sources(self.__callback.sources())
        self.__cmake_creator.append_headers(self.__callback.headers())

        self.__cmake_creator.append_deps(self.__deps)
        self.__cmake_creator.append_defines(self.__defines)

        self.__cmake_creator.create_core_library()

        return self

    def absolute_paths(self):
        return sorted(self.__callback.absolute_paths())

    def view(self):
        """

        :return:
        """
        print("\n".join(self.__cmake_creator.content()))

        return self

    def write_to(self, path: Path):
        """

        :param path:
        :return:
        """
        assert not path.is_dir()

        TextFile(path).open("w+").writeline(self.__cmake_creator.content()).close()

        return self


__all__ = ["DirectoryHarvester"]
