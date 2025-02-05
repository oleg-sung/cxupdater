import setuptools

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


def setup(**attrs):
    cmdclass = attrs.setdefault("cmdclass", {})
    cmdclass.setdefault("build_update", build_update)
    cmdclass.setdefault("build_exe", build_exe)
    attrs.setdefault("executables", [])
    return setuptools.setup(**attrs)


setup.__doc__ = setuptools.setup.__doc__
