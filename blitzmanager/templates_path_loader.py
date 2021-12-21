import os
from .path import Path
from .logger import logger

TEMPLATES_PATH = Path(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
if not TEMPLATES_PATH.is_dir():
    logger.critical(f"Expected blitz cmake templates to be located here : {TEMPLATES_PATH}")
elif TEMPLATES_PATH.is_empty():
    logger.critical(f"Templates directory is empty. {TEMPLATES_PATH}")

__all__ = ["TEMPLATES_PATH"]
