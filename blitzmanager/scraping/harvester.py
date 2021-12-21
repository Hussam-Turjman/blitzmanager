# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from .directory_harvester import DirectoryHarvester
from .directory_parser import DirectoryParserFilter
from ..path import Path
from ..logger import logger


class Harvester(object):
    """
    High level harvester to consume a given directory
    """

    def __init__(self, directory_filter: DirectoryParserFilter, acceptable_extensions: str,
                 dependencies=None, defines=None):

        if dependencies is None:
            dependencies = []
        if defines is None:
            defines = []
        self.__d_filter = directory_filter
        self.__deps = dependencies
        self.__defines = defines
        self.__acceptable_extensions = acceptable_extensions
        self.__directory_harvester = None

    def absolute_paths(self):
        return self.__directory_harvester.absolute_paths()

    def harvest(self, path_to_harvest: Path,
                output_path: Path,
                libname="core_static",
                view=True,
                disabled=True,
                ignore_sub_directories=False,
                object_lib=False):

        if disabled:
            return self
        logger.info(f"Harvesting : {path_to_harvest}")

        self.__directory_harvester = DirectoryHarvester(libname=libname,
                                                        path=path_to_harvest,
                                                        acceptable_extensions=self.__acceptable_extensions,
                                                        directory_filter=self.__d_filter,
                                                        deps=self.__deps,
                                                        defines=self.__defines,
                                                        ignore_sub_directories=ignore_sub_directories,
                                                        object_lib=object_lib
                                                        )

        self.__directory_harvester.parse()

        if view:
            self.__directory_harvester.view()
        else:
            self.__directory_harvester.write_to(output_path)

        return self


__all__ = ["Harvester"]
