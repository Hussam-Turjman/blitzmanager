from blitzmanager import BlitzManager, Path, SupportedManagers
import os

cwd = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    manager_output = Path(cwd, "out")
    build_output = Path(cwd, "out", "dependencies")
    install_path = Path(cwd, "out", "install")
    manager = BlitzManager(manager_output, build_output, install_path, SupportedManagers.NONE)
    manager.parse_arguments()
    manager.initialize_managers()
    manager.build_via_package_manager(["zlib", "sqlite3"])

    manager.build_dependencies()
