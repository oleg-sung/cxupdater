import sys
from enum import Enum
from dataclasses import dataclass
from typing import Union


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
    name: Union[str, None]
    address: Union[str, None]
    version: str


def is_64bit() -> bool:
    return sys.maxsize > 2**32


UPDATER_NAME = 'Updater'
NAMED_PIPE = 'CxUpdater'
ARCH_PREFIX = 'win-amd64' if is_64bit() else 'win32'
