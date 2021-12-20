# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import abc
from ..path import Path


class PackageManager(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def name() -> str:
        """

        :return:
        """

    @staticmethod
    @abc.abstractmethod
    def url() -> str:
        """

        :return:
        """

    @staticmethod
    @abc.abstractmethod
    def version() -> str:
        """

        :return:
        """

    @abc.abstractmethod
    def build(self, dependency: str, *args, **kwargs):
        """

        :param dependency:
        :param args:
        :param kwargs:
        :return:
        """


    @abc.abstractmethod
    def install(self, dependency: str, output_path: Path, *args, **kwargs):
        """

        :param dependency:
        :param output_path:
        :param args:
        :param kwargs:
        :return:
        """

    @abc.abstractmethod
    def uninstall(self, dependency: str, output_path: Path, *args, **kwargs):
        """

        :param dependency:
        :param output_path:
        :param args:
        :param kwargs:
        :return:
        """

    @abc.abstractmethod
    def toolchain_path(self) -> Path:
        """

        :return:
        """

    @abc.abstractmethod
    def source_path(self) -> Path:
        """

        :return:
        """

    @abc.abstractmethod
    def output_path(self) -> Path:
        """

        :return:
        """

    @abc.abstractmethod
    def initialize(self) -> bool:
        """

        :return:
        """


__all__ = ["PackageManager"]
