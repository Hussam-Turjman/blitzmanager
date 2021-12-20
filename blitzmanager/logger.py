# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import logging
import os
import re
import sys
import inspect

from .platform import PLATFORM, OS_NAME, SYS_ARCH


# Global verbose
class Verbose(object):
    def __init__(self):
        self.__verbose = 10

    @property
    def val(self):
        """

        :return:
        """
        return self.__verbose

    @val.setter
    def val(self, val: int):
        """

        :param val:
        :return:
        """

        self.__verbose = val


__verbose = Verbose()
__exit_on_error = True


def set_exit_on_error(val: bool):
    global __exit_on_error
    __exit_on_error = val


def get_exit_on_error():
    return __exit_on_error


def get_global_verbose():
    return __verbose.val


def set_global_verbose(val: int):
    global __verbose
    __verbose.val = val


class Formatter(logging.Formatter):
    def __init__(self, msg):
        """

        :param msg:
        """
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        """

        :param record:
        :return:
        """

        record.msg = reformat_comment(record.msg, add_tab=True)

        return logging.Formatter.format(self, record)


class StreamHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        """

        :param record:
        :return:
        """
        super(StreamHandler, self).emit(record)

        if get_exit_on_error() and record.levelno == logging.ERROR:
            sys.exit(1)


# Custom logger class with multiple destinations
class Logger(logging.Logger):
    FORMAT = "[%(levelname)-7s] %(message)s "

    def __init__(self, name, level=logging.INFO):
        """

        :param name:
        :param level:
        """
        logging.Logger.__init__(self, name, level)

        formatter = Formatter(self.FORMAT)
        console = StreamHandler()
        console.setFormatter(formatter)
        self.addHandler(console)

    def check_verbosity(self, kwargs: dict):
        """

        :param kwargs:
        :return:
        """
        verbose = None

        if "verbose" in kwargs.keys():
            verbose = kwargs.pop("verbose")

        if verbose is not None:
            if verbose > get_global_verbose():
                return False

        return True

    def info(self, msg, *args, **kwargs):
        """

        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        record = inspect.stack()[1]  # 0 represents this line
        # # 1 represents line at caller
        frame = record[0]
        info = inspect.getframeinfo(frame)
        stack_info = f"({os.path.basename(info.filename)}-{info.lineno})"
        msg = f"{msg} {stack_info}"
        if self.check_verbosity(kwargs):
            super(Logger, self).info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """

        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        record = inspect.stack()[1]  # 0 represents this line
        # # 1 represents line at caller
        frame = record[0]
        info = inspect.getframeinfo(frame)
        stack_info = f"({os.path.basename(info.filename)}-{info.lineno})"
        msg = f"{msg} {stack_info}"
        if self.check_verbosity(kwargs):
            super(Logger, self).warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """

        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        record = inspect.stack()[1]  # 0 represents this line
        # # 1 represents line at caller
        frame = record[0]
        info = inspect.getframeinfo(frame)
        stack_info = f"({os.path.basename(info.filename)}-{info.lineno})"
        msg = f"{msg} {stack_info}"
        if self.check_verbosity(kwargs):
            super(Logger, self).error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """

        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        record = inspect.stack()[1]  # 0 represents this line
        # # 1 represents line at caller
        frame = record[0]
        info = inspect.getframeinfo(frame)
        stack_info = f"({os.path.basename(info.filename)}-{info.lineno})"
        msg = f"{msg} {stack_info}"
        if self.check_verbosity(kwargs):
            super(Logger, self).debug(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """

        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        record = inspect.stack()[1]  # 0 represents this line
        # # 1 represents line at caller
        frame = record[0]
        info = inspect.getframeinfo(frame)
        stack_info = f"({os.path.basename(info.filename)}-{info.lineno})"
        msg = f"{msg} {stack_info}"
        if self.check_verbosity(kwargs):
            super(Logger, self).critical(msg, *args, **kwargs)

    def dashed_line(self):
        """

        :return:
        """
        self.info("-" * 40)


logging.setLoggerClass(Logger)

# Global logger
__logger = logging.Logger("blitz-manager")

logger = logging.getLogger(__logger.name)

logger.setLevel(logging.DEBUG)


def reformat_comment(comment: str, add_tab=False):
    """

    :param comment:
    :param add_tab
    :return:
    """

    comment = re.sub(r'\s+', ' ', comment)
    sentence_len = 0
    tmp = []
    for word in comment.split(' '):

        if sentence_len >= 70:
            sentence_len = len(word)
            tmp.append(os.linesep)

        else:
            sentence_len += len(word)

        tmp.append(word)
    comment = " ".join(tmp)

    res = []
    more_than_one_line = False
    for line in comment.split(os.linesep):
        if add_tab and more_than_one_line:
            res.append("\t  {}".format(line.lstrip()))
        else:
            res.append(line.lstrip())
            more_than_one_line = True
    comment = "{}".format(os.linesep).join(res)

    return comment


logger.dashed_line()
logger.info("Platform : {}".format(PLATFORM.platform()))
logger.info("OS Name : {}".format(OS_NAME))
logger.info("Architecture : {}".format(SYS_ARCH))
logger.dashed_line()

__all__ = ["logger", "get_global_verbose", "set_global_verbose", "set_exit_on_error"]
