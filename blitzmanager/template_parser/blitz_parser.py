# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import os
import re

from ..logger import reformat_comment, logger
from ..path import Path


def make_cmake_comment(comment: str):
    """

    :param comment:
    :return:
    """
    comment = reformat_comment(comment)
    res = []
    for line in comment.split(os.linesep):
        res.append("# {}".format(line))
    comment = "{}".format(os.linesep).join(res)

    return comment


def make_cxx_comment(comment: str):
    """

    :param comment:
    :return:
    """
    comment = reformat_comment(comment)

    res = ["/*"]

    for line in comment.split(os.linesep):
        res.append(" * {}".format(line))

    comment = "{}".format(os.linesep).join(res)
    comment = "{}{} */".format(comment, os.linesep)

    return comment


class BlitzParser(object):
    COMMENT_STYLES = ["cmake", "cc", "python", None]

    CC_EXTENSIONS = [".h", ".cc"]
    PYTHON_EXTENSIONS = [".py"]
    CMAKE_EXTENSIONS = [".cmake", ".txt"]

    def __init__(self, entries: dict = None):
        """

        :param entries:
        """
        self.compiler = re.compile(r"!(.*?)!")
        self.__entries = {} if entries is None else entries

    def add_entry(self, key: str, value: str, comment=False):
        """

        :param comment: set to true if the entry is a comment
        :param key:
        :param value:
        :return:
        """
        self.__entries[key] = (str(value), comment)

    def clear(self):
        """

        :return:
        """
        self.__entries.clear()
        self.__entries = {}

    def replace_matches(self, content: str, comment_style="cmake"):
        """

        :param content:
        :param comment_style:
        :return:
        """
        if comment_style not in self.COMMENT_STYLES:
            raise RuntimeError("Invalid comment style \"{}\" ".format(comment_style))

        result = set(self.compiler.findall(content))
        result = [r.strip() for r in result]

        for key in result:
            if key in self.__entries.keys():
                entry, is_comment = self.__entries[key]
                entry = str(entry)
                if is_comment:
                    if comment_style == "cmake" or comment_style == "python":
                        entry = make_cmake_comment(entry)
                    elif comment_style == "cc":
                        entry = make_cxx_comment(entry)
                content = re.sub(r"!\s*%s\s*!" % key, entry, content)
            else:
                raise RuntimeError("Found this match \" {} \" but did not find any entry for it  ".format(key))

        return content

    def parse(self, input_file: str, output_file: str, entries=None):
        """


        :param entries: dictionary of the form  A :{"foo":("entry",False)}
        :param input_file:
        :param output_file:
        :return:
        """

        if entries is not None:
            self.clear()
            self.__entries = entries

        with open(input_file, "r") as f:
            content = f.read()
            f.close()

        with open(output_file, "w+") as f:
            comment_style = None
            path, extension = os.path.splitext(output_file)
            if extension == ".in":
                path, extension = os.path.splitext(path)

            if extension in self.CC_EXTENSIONS:
                comment_style = "cc"
            elif extension in self.CMAKE_EXTENSIONS or extension in self.PYTHON_EXTENSIONS:
                comment_style = "cmake"

            content = self.replace_matches(content, comment_style)
            f.write(content)
            f.close()

    def parse_directory(self, template: Path, output: Path):
        """

        :param template: path to blitz template
        :param output: output directory
        :return:
        """
        if not template.exists():
            raise RuntimeError(" This template \" {} \" does not exist ".format(template))

        if not template.is_dir():
            raise RuntimeError(" This template \" {} \" is not a directory".format(template))

        if template.is_empty():
            raise RuntimeError(" This template \" {} \" is empty".format(template))

        output.make(directory=True, ignore_errors=True)
        logger.info(" Blitz parser : ",verbose=5)
        logger.dashed_line(verbose=5)
        for root, subdirs, files in os.walk(template.path):

            for subdirectory in subdirs:
                subdirectory = os.path.relpath(os.path.join(root, subdirectory), template.path)
                subdirectory = self.replace_matches(subdirectory)
                subdirectory = os.path.join(output.path, subdirectory)
                Path(subdirectory).make(directory=True, ignore_errors=True)

            for file in files:
                input_file = os.path.join(root, file)
                file = os.path.relpath(os.path.join(root, file), template.path)
                if file.endswith(".blitz"):
                    file = os.path.join(output.path, self.replace_matches(file))
                    path, file = os.path.split(file)
                    file = file.replace(".blitz", "")
                    file = os.path.join(path, file)
                    logger.info(f"Input : {input_file}", verbose=5)
                    logger.info(f"Output :  {file}", verbose=5)
                    logger.dashed_line(verbose=5)
                    self.parse(input_file, file)
                else:
                    file = os.path.join(output.path, file)
                    Path(input_file).copy_to(Path(file))


__all__ = ["BlitzParser"]
