# BlitzManager 
BlitzManager is a simple adjustable manager that uses package managers for C/C++ dependencies. It can also
be used to create CMake project templates.



## Quick Start
Here is a simple example for installing dependencies using [vcpkg](https://github.com/microsoft/vcpkg).

```python
from blitzmanager import BlitzManager,Path, SupportedManagers
    
import os

cwd = os.path.dirname(os.path.realpath(__file__))
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
        
```
## Disclaimer
This tool is still under development and should be used with caution.
