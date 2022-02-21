from .path import Path,copy_folder_with_permissions
import os

from .logger import logger
from .arguments_parser import ArgumentsParser
from .runner import Runner
from .flag_observer import FlagObserver
from .cmake import CMakeArguments, CMakeBuilder
from .managers import SupportedManagers
from .main_manager import BlitzManager
from .template_parser import TemplateGenerator
from .templates_path_loader import TEMPLATES_PATH
from .command import Command
from .scraping import DirectoryParserCallback, \
    DirectoryHarvester, \
    AbsolutePathsCollector, \
    DirectoryParserFilter, \
    HeadersExtractorFromDirectory, \
    DirectoryParserFilterOutput, \
    DirectoryParser, \
    CMakeCreator, \
    HeadersCallback, \
    HeadersExtractor, \
    FilterTypes, \
    HeadersReplacer, \
    HeadersCleaner, \
    Harvester, \
    HeadersReplacerCallback, \
    RegexReplacer, \
    RegexReplacerCallback

__all__ = ["logger",
           "Command",
           "TemplateGenerator",
           "CMakeBuilder",
           "CMakeArguments",
           "FlagObserver",
           "ArgumentsParser",
           "Runner",
           "Path",
           "SupportedManagers",
           "BlitzManager",
           "TEMPLATES_PATH",
           "DirectoryParserCallback",
           "DirectoryHarvester",
           "AbsolutePathsCollector",
           "DirectoryParserFilter",
           "HeadersExtractorFromDirectory",
           "DirectoryParserFilterOutput",
           "DirectoryParser",
           "CMakeCreator",
           "HeadersCallback",
           "HeadersExtractor",
           "FilterTypes",
           "HeadersReplacer",
           "HeadersCleaner",
           "Harvester",
           "HeadersReplacerCallback",
           "RegexReplacer",
           "RegexReplacerCallback",
           "copy_folder_with_permissions"
           ]
