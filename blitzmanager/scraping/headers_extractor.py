# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from .headers_replacer import HeadersCleaner, HeadersReplacer
from .directory_parser import DirectoryParserCallback, DirectoryParser, DirectoryParserFilter
from ..path import Path
from ..logger import logger

import os
import re


def replace_with(matches: list):
    if len(matches) == 0:
        return None

    if len(matches) > 1:
        logger.error(f"Unexpected matches : {matches}")
        return None

    return f"{matches[0]}"


class HeadersExtractor(object):
    def __init__(self, input_dir: Path,
                 acceptable_extensions: str,
                 directory_filter: DirectoryParserFilter,
                 exclude_files=None,
                 only_headers=None,
                 exclude_headers_containing=None):
        cleaner = HeadersCleaner({
            r"^.*": replace_with
        })

        self.__replacer = HeadersReplacer(input_dir,
                                          cleaner,
                                          directory_filter=directory_filter,
                                          only_headers=only_headers,
                                          acceptable_extensions=acceptable_extensions,
                                          exclude_headers_containing=exclude_headers_containing,

                                          exclude_files=exclude_files)

    def parse(self):
        self.__replacer.parse()

    def map_values(self):
        return self.__replacer.map_values()


class HeadersExtractorFromDirectoryCallback(DirectoryParserCallback):
    def __init__(self, desired_header_prefix=None):
        self.__existing_headers = {}
        self.__desired_header_prefix = desired_header_prefix

    def existing_headers(self):
        return self.__existing_headers

    def clear(self):
        self.__existing_headers.clear()

    def consume(self, subdirectory: str, file_name: str, relative_path: str, absolute_path: str):
        subdirectory = subdirectory.replace(os.sep, "/")
        relative_path = relative_path.replace(os.sep, "/")

        if subdirectory != ".":
            relative_path = f"{subdirectory}/" + relative_path

        if self.__desired_header_prefix is not None:
            relative_path = f"{self.__desired_header_prefix}/{relative_path}"

        assert relative_path not in self.__existing_headers.keys(), "Key already exist"

        self.__existing_headers[relative_path] = absolute_path


class HeadersExtractorFromDirectory(object):
    def __init__(self, extractor: HeadersExtractor,
                 input_dir: Path,
                 directory_filter: DirectoryParserFilter,
                 exclude_files=None,
                 desired_header_prefix=None):

        self.__extractor = extractor
        self.__callback = HeadersExtractorFromDirectoryCallback(desired_header_prefix)
        self.__invalid_includes = []
        self.__parser = DirectoryParser(input_dir, self.__callback,
                                        filter_output=directory_filter(),
                                        acceptable_extensions=r".*\.(h|inc)$",
                                        exclude_files=exclude_files)

    def existing_headers(self):
        return self.__callback.existing_headers()

    def invalid_includes(self):
        return self.__invalid_includes

    def parse(self, view=True, to_ignore_regex=None):
        self.__callback.clear()
        self.__invalid_includes.clear()
        self.__parser.parse()

        self.__extractor.parse()

        for map_value in self.__extractor.map_values():
            if map_value.old_header not in self.__callback.existing_headers().keys():
                if to_ignore_regex is not None:
                    compiler = re.compile(to_ignore_regex)
                    if len(compiler.findall(map_value.old_header)) > 0:
                        continue
                if view:
                    print(" {:<50} {} in {}".format(map_value.old_header, "invalid include", map_value.path))

                self.__invalid_includes.append(map_value)


__all__ = ["HeadersExtractor", "HeadersExtractorFromDirectory"]
