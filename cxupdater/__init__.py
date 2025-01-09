import setuptools

from cx_Freeze import Distribution
from cx_Freeze.command import build_exe

from .version_parser import PackageParser
from .update_finder import CxUpdater, CxDelegateInterface
from .commands.build_update import BuildUpdate as build_update
from .pipe_connecter import PipeWriter, PipeReceiver, UpdateInstallerMessageHandler
from .config import *
from .utils import *

__all__ = [
    'setup',
    'PackageParser',
    'CxUpdater',
    'CxDelegateInterface',
    'PipeWriter',
    'PipeReceiver',
    'UpdateInstallerMessageHandler',
    'build_update',
    '__version__',
]

__version__ = '0.1.0'


def _add_command_class(command_classes, name, cls):
    if name not in command_classes:
        command_classes[name] = cls


def setup(**attrs):
    attrs.setdefault("distclass", Distribution)
    command_classes = attrs.setdefault("cmdclass", {})
    _add_command_class(command_classes, "build_update", build_update)
    _add_command_class(command_classes, "build_exe", build_exe)
    setuptools.setup(**attrs)


setup.__doc__ = setuptools.setup.__doc__
