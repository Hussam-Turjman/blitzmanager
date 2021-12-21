# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from ..platform import PLATFORM, OS_NAME, SYS_ARCH


class CMakeCreator(object):
    """
    CMakeLists.txt generator
    """
    params = ["NAME", "COPTS", "SRCS", "HDRS", "DEFINES", "PUBLIC", "DEPS", "OBJECT_LIB"]

    def __init__(self, libname: str, object_lib=False):
        self.__name = libname
        self.__object_lib = object_lib
        self.__headers = []
        self.__sources = []
        self.__defines = []
        self.__deps = []
        self.__content = []
        self.reset()

    def reset(self):
        self.__deps.clear()
        self.__sources.clear()
        self.__headers.clear()
        self.__content.clear()
        self.__content = ["# Auto Generated File DO NOT EDIT\n\n\n"]

    def set_macro(self, name: str, content: list):
        self.__content.append(f"SET({name}")
        self.__content += content
        self.__content.append(")")

    def append_headers(self, headers: list):
        self.__headers += headers

    def append_sources(self, sources: list):
        self.__sources += sources

    def append_defines(self, defines: list):
        self.__defines += defines

    def append_deps(self, deps: list):
        self.__deps += deps

    def content(self):
        return self.__content

    def sources(self):
        return self.__sources

    def headers(self):
        return self.__headers

    def deps(self):
        return self.__deps

    def defines(self):
        return self.__defines

    def create_core_library_for_testing(self, name: str, headers: list, sources: list, deps: list, defines: list):

        from_idx = len(self.__content)

        self.__content += ["core_cc_library(", "NAME", f"{name}", "HDRS"]

        for hdr in sorted(headers):
            self.__content.append("\"{}\"".format(hdr))

        self.__content.append("COPTS")
        self.__content.append("${CORE_DEFAULT_COPTS}")
        self.__content.append("SRCS")

        for src in sorted(sources):
            self.__content.append("\"{}\"".format(src))

        self.__content.append("DEFINES")
        for d in sorted(defines):
            self.__content.append(d)

        self.__content.append("DEPS")
        self.__content.append("Threads::Threads")

        for dep in deps:
            self.__content.append(dep)

        self.__content.append("PUBLIC")
        self.__content.append("TESTONLY")
        self.__content.append(")")

        for i in range(from_idx + 1, len(self.__content) - 1):
            if self.__content[i] not in self.params:
                self.__content[i] = "\t\t {}".format(self.__content[i])
            else:
                self.__content[i] = "\t\t{}".format(self.__content[i])

        self.__content.append("\n")
        self.__content.append(f"# Sources       : {len(sources)}")
        self.__content.append(f"# Headers       : {len(headers)}")
        self.__content.append(f"# Deps          : {len(deps)}")
        self.__content.append(f"# Defines       : {len(defines)}")
        self.__content.append("\n\n")
        return self

    def create_unittest(self, name: str, sources: list, headers: list, deps: list, defines: list):

        from_idx = len(self.__content)

        self.__content += ["core_cc_test(", "NAME", f"{name}", "HDRS"]

        for hdr in headers:
            self.__content.append("\"{}\"".format(hdr))

        self.__content.append("COPTS")
        self.__content.append("${CORE_DEFAULT_COPTS}")
        self.__content.append("SRCS")

        for src in sources:
            self.__content.append("\"{}\"".format(src))

        self.__content.append("DEFINES")
        for d in defines:
            self.__content.append(d)
        self.__content.append("DEPS")
        self.__content.append("Threads::Threads")

        for dep in deps:
            self.__content.append(dep)

        self.__content.append("PUBLIC")
        self.__content.append(")")

        for i in range(from_idx + 1, len(self.__content) - 1):
            if self.__content[i] not in self.params:
                self.__content[i] = "\t\t {}".format(self.__content[i])
            else:
                self.__content[i] = "\t\t{}".format(self.__content[i])

        return self

    def create_core_library(self):
        """

        :return:
        """
        win_sources = []
        posix_sources = []
        linux_sources = []

        for i, s in enumerate(self.__sources):
            if "_win.cc" in s:
                win_sources.append(self.__sources.pop(i))
            if "_linux.cc" in s:
                linux_sources.append(self.__sources.pop(i))
            if "_posix.cc" in s:
                posix_sources.append(self.__sources.pop(i))

        win_specific = ["if (IS_WIN)", "set(WINDOWS_SOURCES"]
        for src in sorted(win_sources):
            win_specific.append("\t\t\"{}\"".format(src))
        win_specific.append(")")
        win_specific.append("endif ()")

        linux_specific = ["if (IS_LINUX)", "set(LINUX_SOURCES"]
        for src in sorted(linux_sources):
            linux_specific.append("\t\t\"{}\"".format(src))
        linux_specific.append(")")
        linux_specific.append("endif ()")

        posix_specific = ["if (IS_POSIX)", "set(POSIX_SOURCES"]
        for src in sorted(posix_sources):
            posix_specific.append("\t\t\"{}\"".format(src))
        posix_specific.append(")")
        posix_specific.append("endif ()")

        self.__content += win_specific
        self.__content += linux_specific + posix_specific

        from_idx = len(self.__content)

        self.__content += ["core_cc_library(", "NAME", f"{self.__name}", "HDRS"]

        for hdr in sorted(self.__headers):
            if "_mac.h" in hdr:
                self.__content.append("# \"{}\"".format(hdr))
            else:
                self.__content.append("\"{}\"".format(hdr))

        self.__content.append("COPTS")
        self.__content.append("${CORE_DEFAULT_COPTS}")
        self.__content.append("SRCS")

        for src in sorted(self.__sources):
            if "_mac.cc" in src:
                self.__content.append("# \"{}\"".format(src))
            else:
                self.__content.append("\"{}\"".format(src))

        self.__content.append("\"{}\"".format("${WINDOWS_SOURCES}"))
        self.__content.append("\"{}\"".format("${POSIX_SOURCES}"))
        self.__content.append("\"{}\"".format("${LINUX_SOURCES}"))

        self.__content.append("DEFINES")
        for d in sorted(self.__defines):
            self.__content.append(d)
        self.__content.append("DEPS")
        self.__content.append("Threads::Threads")

        for dep in self.__deps:
            self.__content.append(dep)

        self.__content.append("PUBLIC")
        if self.__object_lib:
            self.__content.append("OBJECT_LIB")
        self.__content.append(")")

        for i in range(from_idx + 1, len(self.__content) - 1):
            if self.__content[i] not in self.params:
                self.__content[i] = "\t\t {}".format(self.__content[i])
            else:
                self.__content[i] = "\t\t{}".format(self.__content[i])
        self.__content.append("\n")

        self.__content.append("target_link_libraries(%s PUBLIC ${CMAKE_DL_LIBS})" % self.__name)

        self.__content.append("\n")
        self.__content.append(f"# Sources       : {len(self.__sources)}")
        self.__content.append(f"# Headers       : {len(self.__headers)}")
        self.__content.append(f"# Deps          : {len(self.__deps)}")
        self.__content.append(f"# Defines       : {len(self.__defines)}")
        self.__content.append(f"# Platform      : {PLATFORM.platform()}")
        self.__content.append(f"# OS            : {OS_NAME}")
        self.__content.append(f"# Architecture  : {SYS_ARCH}")


__all__ = ["CMakeCreator"]
