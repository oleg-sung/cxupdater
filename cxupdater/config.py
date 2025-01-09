import sys
from enum import Enum
from dataclasses import dataclass
from typing import Union

from packaging.version import Version


class UpdaterStatus(Enum):
    STARTING = 'Starting'
    PROCESSING = 'Processing'
    FINISHED = 'Finished'
    FAILED = 'Failed'
    ERROR = 'Error'
    EXITED = 'Exited'
    NOT_FOUND = 'Not Found'


@dataclass(frozen=True)
class UpdatePackage:
    version: str
    name: Union[str, None] = None
    address: Union[str, None] = None
    arch: Union[str, None] = None

    def __gt__(self, other: 'UpdatePackage') -> bool:
        if self.arch != other.arch:
            return False
        return Version(self.version) > Version(other.version)


def is_64bit() -> bool:
    return sys.maxsize > 2**32


UPDATER_NAME = 'Updater'
NAMED_PIPE = 'CxUpdater'
ARCH_PREFIX = 'win-amd64' if is_64bit() else 'win32'
