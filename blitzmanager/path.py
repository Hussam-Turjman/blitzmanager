# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import os
import shutil

from .logger import logger
import zipfile


class Path(object):
    def __init__(self, path: str, *paths):
        assert type(path) is str
        for p in paths:
            assert type(p) is str

        self.__path = os.path.join(path, *paths)

    def is_file(self):
        return os.path.isfile(self.__path)

    def dirname(self):
        return os.path.dirname(self.__path)

    def copy(self):
        return Path(self.__path)

    def split(self):
        return self.path.split(os.sep)

    def file_name(self):
        return os.path.basename(self.__path)

    def relative_path(self, folder: str):
        return os.path.relpath(self.__path, folder)

    def join(self, *args):
        """

        :param args:
        :return:
        """
        self.__path = os.path.join(self.__path, *args)
        return self

    @property
    def path(self):
        return self.__path

    def is_abs(self):
        if self.exist():
            return os.path.isabs(self.__path)
        return False

    def exist(self):
        """

        :return:
        """
        return os.path.exists(self.path)

    def is_empty(self):
        """

        :return:
        """
        if self.is_dir():
            if len(os.listdir(self.path)) == 0:
                return True

        return False

    def is_dir(self):
        """

        :return:
        """
        if self.exist():
            return os.path.isdir(self.path)
        return False

    def remove(self, ignore_errors=True):
        """

        :return:
        """
        exception = None
        if self.is_dir():
            try:
                shutil.rmtree(self.path, ignore_errors=ignore_errors)
            except Exception as exp:
                exception = str(exp)
        else:
            try:
                os.remove(self.path)
            except Exception as exp:
                exception = str(exp)

        if exception is not None:
            if ignore_errors:
                logger.critical(exception)
            else:
                logger.error(exception)
        else:
            logger.info("The path \"{}\" has been removed.".format(self.path))
            return True
        return False

    def make(self, override=False, directory=False, ignore_errors=False):
        """
        :param ignore_errors :
        :param directory : whether a directory or file should be created
        :param override : if true remove the old path.
        :return:
        """
        exist = self.exist()
        if exist and not override:
            msg = "The path \"{}\" already exist and therefore will not be created.".format(self.path)
            if ignore_errors:
                logger.warning(msg)
            else:
                logger.error(msg)
            return False
        else:
            if exist and override:
                self.remove(ignore_errors=False)

            if directory:
                os.makedirs(self.path, exist_ok=True)
            else:
                open(self.path, "w+").close()

            logger.info("The path \"{}\" has been created".format(self.path))

        return True

    def __copy_file(self, des: str, source=None):
        """

        :param des:
        :return:
        """
        if source is None:
            source = self.path
        try:
            shutil.copyfile(source, des)
        except Exception as exp:
            logger.error("Failed to copy a file from {} to {}. {}".format(source, des, str(exp)))

        logger.info("Copying {} to {} ".format(source, des), verbose=5)

    def copy_to(self, destination):
        """

        :param destination:
        :return:
        """
        assert isinstance(destination, Path)

        if not self.exist():
            logger.error(f"This path {self.path} does not exist and cannot be copied to {destination}")
            return False

        if not self.is_dir():
            self.__copy_file(destination.path)
            return True

        destination.make(directory=True, ignore_errors=True)

        source = self.path
        target = destination.path

        for root, subdirs, files in os.walk(source):

            for subdirectory in subdirs:
                subdirectory = os.path.relpath(os.path.join(root, subdirectory), source)

                subdirectory = os.path.join(target, subdirectory)
                Path(subdirectory).make(directory=True)

            for file in files:
                input_file = os.path.join(root, file)
                file = os.path.relpath(os.path.join(root, file), source)
                file = os.path.join(target, file)
                self.__copy_file(file, source=input_file)

        return True

    def unzip(self, output_dir):
        """

        :param output_dir:
        :return:
        """

        logger.info(f"Extracting {self.path} to {output_dir}")
        try:
            with zipfile.ZipFile(self.path, 'r') as zip_ref:
                zip_ref.extractall(output_dir.path)
            return True
        except Exception as e:
            logger.error(f"Failed to extract {self.path} to {output_dir}. Error : {e}")

    def __str__(self):
        """

        :return:
        """
        return self.path


__all__ = ["Path"]
