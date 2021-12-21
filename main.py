# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

from blitzmanager import BlitzManager, \
    Path, SupportedManagers, \
    TemplateGenerator, TEMPLATES_PATH, DirectoryParser
import os

cwd = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':

    manager_output = Path(cwd, "out")
    build_output = Path(cwd, "out", "dependencies")
    install_path = Path(cwd, "out", "install")
    flags = {
        "--output_dir": {
            "required": False,
            "default": None,
            "type": str,
            "help": "Chose another output directory."
        }
    }
    manager = BlitzManager()

    manager.add_flags(flags)
    manager.parse_arguments()
    manager.create_template("centauri", TemplateGenerator.default_config(), manager_output)
    exit(0)

    if manager["output_dir"] is not None:
        manager_output = Path(manager["output_dir"])
        assert not manager_output.is_file()
        assert manager_output.is_abs(check_if_exists=False)
        build_output = Path(manager_output.path, "dependencies")
        install_path = Path(manager_output.path, "install")
    manager.initialize(manager_output, build_output, install_path, SupportedManagers.VCPKG)
    manager.initialize_managers()
    manager.build_via_package_manager(["zlib", "sqlite3"])

    manager.build_dependencies()
