# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import collections
import re
from abc import abstractmethod
from operator import is_not
from functools import partial
from .directory_parser import DirectoryParser, DirectoryParserCallback, DirectoryParserFilter
from ..logger import logger
from ..path import Path


class HeadersCallback(DirectoryParserCallback):
    """
    Look for all #include statements in a given directory
    and store the headers in res
    """

    def __init__(self, only_headers, exclude_headers_containing):
        self.compiler = re.compile(r"\s*#include\s*\"(.*?)\"\s*")
        self._res = {}
        # look only for these headers (regex's)
        self.__only_headers = only_headers
        # ignore headers containing a value from this list
        self.__exclude_headers_containing = exclude_headers_containing

    @property
    def res(self):
        return collections.OrderedDict(sorted(self._res.items()))

    def consume(self, subdirectory: str, file_name: str, relative_path: str, absolute_path: str):

        f = open(absolute_path, "r")
        content = f.read()
        content = list(set(self.compiler.findall(content)))
        f.close()

        if self.__only_headers is not None:
            to_add = []

            for only in self.__only_headers:
                compiler = re.compile(only)
                for h in content:
                    for v in compiler.findall(h):
                        to_add.append(v)

            if len(to_add) > 0:
                self._res[absolute_path] = to_add

            return

        to_remove = []
        if self.__exclude_headers_containing is not None:
            for to_exclude in self.__exclude_headers_containing:
                for h in content:
                    if to_exclude in h:
                        to_remove.append(h)

        content = list(set(content) - set(to_remove))

        self._res[absolute_path] = content


class HeadersReplacerCallback(object):
    """
    Headers replacer observer.
    clean_header gets a header as an input and can then
    decide to either discard it by returning None or return a replacement header.
    """

    @abstractmethod
    def clean_header(self, h: str):
        """

        :param h:
        :return:
        """


class HeadersCleaner(HeadersReplacerCallback):
    """
    Helper class to clean the headers with regex's and callbacks.
    """

    def __init__(self, matches: dict):
        self.__matches = matches

    def clean_header(self, header: str):
        for regex in self.__matches.keys():
            compiler = re.compile(regex)
            ret = self.__matches[regex](compiler.findall(header))
            if ret is None:
                continue
            else:
                return ret
        return None


class MapValue(object):
    def __init__(self, old_header, new_header, path):
        self.old_header = old_header
        self.new_header = new_header
        self.path = path

    def __le__(self, other):
        return self.old_header <= other.old_header

    def __lt__(self, other):
        return self.old_header < other.old_header

    def __str__(self):
        return f"old_header: {self.old_header} new_header: {self.new_header} absolute_path: {self.path}"


class MapValueList(list):
    def __str__(self):
        return "MapValueList"


class HeadersReplacer(object):
    """
    Takes a directory as an input a replaces specific
    header includes with custom modified values.
    """

    def __init__(self, input_dir: Path, callback: HeadersReplacerCallback,
                 acceptable_extensions: str,
                 directory_filter: DirectoryParserFilter,
                 exclude_files=None,
                 only_headers=None,
                 exclude_headers_containing=None):

        self.__input_dir = input_dir
        self.__cleaner_callback = callback
        self.__callback = HeadersCallback(only_headers, exclude_headers_containing)
        self.__parser = DirectoryParser(input_dir=input_dir,
                                        callback=self.__callback,
                                        acceptable_extensions=acceptable_extensions,
                                        filter_output=directory_filter(),
                                        exclude_files=exclude_files)
        self.__headers_map = {}
        self.__lookup_paths = []
        self.__map_values = []
        self.replaced_counter = 0

    def handle_path(self, path):
        for v in self.__callback.res[path]:
            ret = self.__cleaner_callback.clean_header(v)
            if ret is None:
                continue

            return MapValue(old_header=v, new_header=ret, path=path)
        return None

    def handle_map_value(self, m: MapValue):
        self.__lookup_paths.append(m.path)
        self.__headers_map[m.old_header] = m.new_header

    def parse(self, disabled=True):
        if disabled:
            return self

        self.replaced_counter = 0
        self.__headers_map.clear()
        self.__callback.res.clear()
        self.__lookup_paths.clear()
        self.__map_values.clear()
        self.__parser.parse()
        logger.info("Headers replacer started")
        worker = self.handle_path

        res = list(map(worker, self.__callback.res.keys()))

        map_values = list(filter(partial(is_not, None), res))
        total_map_values = len(map_values)
        for m in map_values:
            self.__map_values.append(m)
            self.handle_map_value(m)

        logger.info(f"Headers replacer is done total_map_values = {total_map_values}")
        return self

    def map_values(self):
        return MapValueList(self.__map_values)

    def view(self, view_path_relative_to=None):
        logger.info(f"Input directory : {self.__input_dir}")
        for m in sorted(self.__map_values):
            path = Path(m.path).relative_path(view_path_relative_to) if view_path_relative_to is not None else Path(
                m.path).file_name()
            print("{:<65} --> {:<60} ({})".format(m.old_header, m.new_header, path))

        logger.info(f"Matches : {len(self.__map_values)}")
        return self

    def handle_file(self, path: str):
        f = open(path, "r")
        content = f.read()
        f.close()
        has_been_replaced = False

        for k in self.__headers_map.keys():

            compiler = re.compile(r"\s*#include\s*\"" + k + r"\"\s*")
            matches = list(set(compiler.findall(content)))
            has_been_replaced = True # len(matches) > 0
            for found in matches:
                found = found.strip("\n")
                content = content.replace(found, found.replace(k, self.__headers_map[k]))
                # logger.info(f"Found : {found} in {path}")

            # print("{:<60} --> {:<50} ".format(k, self.__headers_map[k]))
            pass

        if has_been_replaced:
            f = open(path, "w+")
            f.write(content)
            f.close()
            self.replaced_counter += 1
            logger.info(f"Done replacing in {path}")

    def do_replace(self):
        worker = self.handle_file

        list(map(worker, self.__lookup_paths))

        logger.info(f"Header Replacer is done overwritten_files = {self.replaced_counter}")
        return self


__all__ = ["HeadersReplacer", "HeadersReplacerCallback", "HeadersCallback", "HeadersCleaner"]
