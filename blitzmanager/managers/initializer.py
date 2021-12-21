# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.
from typing import List

from ..path import Path
from .vcpkg import VcpkgManager
from .manager import PackageManager
from .download import fetch

from ..logger import logger


class ManagerInitializer(object):
    __supported_managers = [VcpkgManager]
    managers: List[PackageManager]

    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.managers = []

    @staticmethod
    def supported_managers() -> List[str]:
        """

        :return:
        """

        return [f" name: {m.name()}, version: {m.version()}, url: {m.url()}" for m in
                ManagerInitializer.__supported_managers]

    def download(self, override=False):
        """

        :return:
        """
        for m in ManagerInitializer.__supported_managers:
            path = Path(self.output_path.path, f"{m.name()}.zip")
            output_dir = Path(self.output_path.path, f"{m.name()}_extracted")

            if path.exists() and not override:
                logger.info(f"{path} already exist",verbose=10)
                if output_dir.exists():
                    logger.info(f"{output_dir} already exist",verbose=10)
                    self.managers.append(m(input_path=output_dir))
                    continue
                if not path.unzip(output_dir):
                    break
            if not fetch(m.url(), path):
                break
            elif not path.unzip(output_dir):
                break
            self.managers.append(m(input_path=output_dir))
        return self

    def build(self):
        """

        :return:
        """
        for m in self.managers:
            if not m.initialize():
                logger.error(f"Failed to initialize the package manager : {m.name()}",verbose=0)
                return self
        return self


__all__ = ["ManagerInitializer"]
