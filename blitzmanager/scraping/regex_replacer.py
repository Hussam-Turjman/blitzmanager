# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from abc import abstractmethod

from .directory_parser import DirectoryParserCallback, DirectoryParser, DirectoryParserFilter
from ..path import Path
import re


class RegexReplacerCallback(object):
    @abstractmethod
    def consume(self, absolute_path: str, content: str, regex: str, matches: list):
        pass


class ParserCallback(DirectoryParserCallback):
    def __init__(self, regex_list: list, callback: RegexReplacerCallback):
        self.__regex_list = regex_list
        self.__callback = callback

    def consume(self, subdirectory: str, file_name: str, relative_path: str, absolute_path: str):
        f = open(absolute_path, "r")
        content = f.read()
        f.close()
        for regex in self.__regex_list:
            compiler = re.compile(regex)
            found = compiler.findall(content)
            if len(found) > 0:
                self.__callback.consume(absolute_path, content, regex, found)


class RegexReplacer(object):
    def __init__(self, input_dir: Path,
                 acceptable_extensions: str,
                 directory_filter: DirectoryParserFilter,
                 regex_list: list,
                 callback: RegexReplacerCallback):
        self.__input_dir = input_dir
        self.__callback = ParserCallback(regex_list, callback)
        self.__parser = DirectoryParser(input_dir=input_dir,
                                        callback=self.__callback,
                                        acceptable_extensions=acceptable_extensions,
                                        filter_output=directory_filter())

    def parse(self, disabled=True):
        if disabled:
            return self
        self.__parser.parse()
        return self


__all__ = ["RegexReplacer", "RegexReplacerCallback"]
