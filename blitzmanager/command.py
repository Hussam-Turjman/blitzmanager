# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import json
import os
import subprocess

from .logger import logger


class Command(object):
    def __init__(self, *args, program=None):
        """

        :param program: path to an executable
        """

        self.program = program

        self.args = args

    def read_arguments(self, path: str):
        """

        :param path: path to json file
        :return:
        """
        with open(path, "r") as f:
            self.args = json.load(f)
            f.close()

        return self

    def add_arguments(self, *args):
        """

        :param args:
        :return:
        """
        self.args += args

        return self

    def execute(self, cwd=None, check=True):
        """

        :param cwd: working directory for the program
        :param check: fail if the program returned a status code other than zero
        :return:
        """
        logger.dashed_line(verbose=10)

        args = " ".join(self.args)
        msg = "Executing : {} {}".format(self.program, args)

        logger.info(msg,verbose=10)
        logger.info("Working directory : {}".format(cwd),verbose=10)

        logger.dashed_line(verbose=10)

        args = [self.program]
        args += self.args

        subprocess.run(args, cwd=cwd, check=check)
        logger.info(os.linesep,verbose=10)

        return self


__all__ = ["Command"]
