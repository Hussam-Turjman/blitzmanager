# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.


from .manager import PackageManager
from ..path import Path
from ..command import Command
from ..platform import PLATFORM
from ..logger import logger
from .supported_managers import SupportedManagers


class VcpkgManager(PackageManager):
    vcpkg_path: Path

    @staticmethod
    def type() -> SupportedManagers:
        """

        :return:
        """
        return SupportedManagers.VCPKG

    @staticmethod
    def name() -> str:
        return "Vcpkg"

    @staticmethod
    def url() -> str:
        return f"https://github.com/microsoft/vcpkg/archive/refs/tags/{VcpkgManager.version()}.zip"

    @staticmethod
    def version() -> str:
        return "2023.08.09"

    def __init__(self, input_path: Path):
        assert input_path.is_dir()
        self.input_path = input_path
        self.__output_path = Path(self.input_path.path, "out")
        # x64-linux
        # x64-windows-static
        # x64-windows
        # x86-windows
        self.vcpkg_path = Path("")
        self.__toolchain_path = Path("")
        self.__install_path = Path("")
        if PLATFORM.is_windows():
            self.target = "x64-windows-static"
        elif PLATFORM.is_linux():
            self.target = "x64-linux"
        else:
            raise NotImplemented("Unsupported platform")

    def build(self, dependency: str, *args, **kwargs):
        """

        :param dependency:

        :param args:
        :param kwargs:
        :return:
        """
        Command("install", "{}:{}".format(dependency, self.target),
                program=Path(self.vcpkg_path.path).path
                ).execute(cwd=self.vcpkg_path.dirname())
        return self

    def install(self, dependency: str, output_path: Path, *args, **kwargs):
        """

        :param dependency:
        :param output_path:
        :param args:
        :param kwargs:
        :return:
        """
        return self

    def uninstall(self, dependency: str, output_path: Path, *args, **kwargs):
        """

        :param dependency:
        :param output_path:
        :param args:
        :param kwargs:
        :return:
        """
        return self

    def toolchain_path(self) -> Path:
        """

        :return:
        """
        return self.__toolchain_path

    def source_path(self) -> Path:
        """

        :return:
        """
        return self.input_path

    def output_path(self) -> Path:
        """

        :return:
        """
        return self.__output_path

    def install_path(self) -> Path:
        """

        :return:
        """
        return self.__install_path

    def initialize(self) -> bool:
        """

        :return:
        """
        path = Path(self.input_path.path, f"vcpkg-{self.version()}")
        assert path.exists()
        vcpkg_bin = Path(path.path, "vcpkg")
        self.__install_path = Path(path.path, "installed", self.target)
        self.__toolchain_path = Path(path.path,
                                     "scripts",
                                     "buildsystems",
                                     "vcpkg.cmake")
        self.vcpkg_path = vcpkg_bin.copy()
        if vcpkg_bin.exists():
            logger.info(f"vcpkg is already built and located here : {vcpkg_bin.path}", verbose=10)
            return True
        bootstrap = path.copy()

        if PLATFORM.is_linux() or PLATFORM.is_darwin():
            bootstrap.join("bootstrap-vcpkg.sh")
            Command("+x", bootstrap.path, program="chmod").execute()
        elif PLATFORM.is_windows():
            bootstrap.join("bootstrap-vcpkg.bat")
        else:
            raise RuntimeError("Unsupported platform")

        Command("-disableMetrics",
                program=bootstrap.path).execute(cwd=path.path)
        assert Path(path.path, "vcpkg").exists()
        return True


__all__ = ["VcpkgManager"]
