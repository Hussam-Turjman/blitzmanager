# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import json
import os
from datetime import datetime

from .blitz_parser import BlitzParser
from ..logger import logger
from ..path import Path


class TemplateGenerator(object):

    def __init__(self, entries: dict):
        """

        :param entries:
        """

        self.parser = BlitzParser(self.check_comments(entries))
        self.entries = entries
        current_date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        blitz_notice = """
        Auto generated file by BlitzManager {}. 
        BlitzManager is a tool for generating cmake templates, 
        written by (Mohammed Hussam Al Turjman, hussam.turjman@gmail.com).
        For more information please visit https://github.com/Hussam-Turjman/blitzmanager""".format(current_date)

        major, minor, patch = tuple(entries["PROJECT_VERSION"].split('.'))

        self.project_name_lower = entries["PROJECT_NAME"].lower()
        self.project_name_upper = entries["PROJECT_NAME"].upper()
        self.parser.add_entry("BLITZ_NOTICE", blitz_notice, comment=True)
        self.parser.add_entry("PROJECT_NAME_LOWER", self.project_name_lower)
        self.parser.add_entry("PROJECT_NAME_CAPITAL", self.project_name_upper)
        self.parser.add_entry("VERSION_MAJOR", major)
        self.parser.add_entry("VERSION_MINOR", minor)
        self.parser.add_entry("VERSION_PATCH", patch)

    @staticmethod
    def list_available_templates(templates_root_dir: Path):
        """

        :param templates_root_dir:
        :return:
        """
        if not templates_root_dir.exists():
            logger.critical(f"Templates directory does not exists. {templates_root_dir}")
            return
        if templates_root_dir.is_empty():
            logger.critical(F"Templates directory is empty. {templates_root_dir}")
            return

        def callback(root, subdirs, files):
            for template in subdirs:
                print(f"Template : {template}")

        print(f"\n\nAvailable CMake templates located at {templates_root_dir} : \n\n")
        templates_root_dir.walk(callback=callback, recursive=False)
        print()

    def generate(self):
        """

        :return:
        """
        template = self.entries["template_path"]
        if not template.exists():
            logger.error(" Looking for this template \"{}\" but the path does not exist.".format(template))
            return False

        self.parser.parse_directory(template, self.entries["build_dir"])

        out = self.entries.copy()
        out.pop("build_dir", None)
        out.pop("template_path", None)

        with open(self.entries["build_dir"].join("config.json").path, "w+") as f:
            json.dump(obj=out, fp=f, ensure_ascii=True,
                      indent=4, sort_keys=True)

            f.close()

        return True

    @staticmethod
    def check_comments(entries: dict):
        """

        :param entries:
        :return:
        """
        out = {}

        def is_comment(key: str):
            if key.upper() == "DESCRIPTION":
                return True
            if key.upper() == "URL":
                return True
            if key.upper() == "ORGANISATION":
                return True
            if key.upper() == "COPYRIGHT":
                return True
            return False

        for key in entries.keys():
            out[key] = (entries[key], is_comment(key))
        return out

    @staticmethod
    def default_config():
        """

        :return:
        """
        return json.loads("""
  {
  "AUTHOR":"Mohammed Hussam Al Turjman",
  "DESCRIPTION": "Blitz Server",
  "URL":"www.example.com",
  "ORGANISATION":"Eternity",
  "CMAKE_CXX_STANDARD": 20,
  "CMAKE_C_STANDARD":11,
  "CMAKE_MINIMUM_REQUIRED_VERSION": 3.17,
  "COPYRIGHT": "Copyright (c) 2021 The Blitz project Authors. All rights reserved. Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.",
  "LIBNAME": "blitz_server",
  "PROJECT_NAME": "BlitzServer",
  "PROJECT_VERSION": "0.0.0",
  "YEAR":2021
}
        """)


__all__ = ["TemplateGenerator"]
