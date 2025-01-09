import time
from abc import ABC, abstractmethod
from typing import Union, Dict, Callable

import requests
from packaging.version import Version

from cxupdater.pipe_connecter import PipeReceiver
from cxupdater.config import UpdaterStatus, NAMED_PIPE, UpdatePackage, ARCH_PREFIX
from cxupdater.utils import run_execute, get_update_installer_path, create_message_dict
from cxupdater.version_parser import PackageParser


class CxDelegateInterface(ABC):

    """
    Delegate interface
    """

    @abstractmethod
    def do_start_update(self, message: dict) -> None:
        pass

    @abstractmethod
    def do_processing_update(self, message: dict) -> None:
        pass

    @abstractmethod
    def do_not_found_update(self, message: dict) -> None:
        pass

    @abstractmethod
    def do_exited_update(self, message: dict) -> None:
        pass

    @abstractmethod
    def do_error_update(self, message: dict) -> None:
        pass

    @abstractmethod
    def do_finished_update(self, message: dict) -> None:
        pass


class CxUpdater:
    """
    Class for auto-updating an app
    """

    def __init__(self, toml_url: str, version: str, delegate: CxDelegateInterface, verify: bool = True) -> None:
        self._version = version
        self._toml_url = toml_url
        self._download_latest_version_url = None
        self._verify = verify
        if isinstance(delegate, CxDelegateInterface):
            self._delegate = delegate
        else:
            raise TypeError('delegate must be instance of CxDelegateInterface')
        self.version_parser = PackageParser()
        self._arh = ARCH_PREFIX
        self._named_pipe = PipeReceiver(NAMED_PIPE)
        self.delegate_mapping: Dict[str, Callable[[dict], None]] = {
            UpdaterStatus.STARTING.value: self._delegate.do_start_update,
            UpdaterStatus.PROCESSING.value: self._delegate.do_processing_update,
            UpdaterStatus.EXITED.value: self._delegate.do_exited_update,
            UpdaterStatus.NOT_FOUND.value: self._delegate.do_not_found_update,
            UpdaterStatus.FINISHED.value: self._delegate.do_finished_update,
            UpdaterStatus.ERROR.value: self._delegate.do_error_update,
        }

    def do_auto_updater(self) -> UpdaterStatus:
        """
        Process of automatic application updates.

        Returns:
            One out of UpdaterStatus values
        """
        update_package = self.search_update()
        if not self.need_to_update(update_package.version):
            message = create_message_dict(
                UpdaterStatus.NOT_FOUND.value, "Update not found",
                url=self._toml_url
            )
            self.delegate_mapping[UpdaterStatus.NOT_FOUND.value](message)
            return UpdaterStatus.NOT_FOUND
        else:
            self._download_latest_version_url = update_package.address
            status = self.start_installer()
            if status != UpdaterStatus.STARTING:
                return status
            status = self.listening_update_installer()
            return status

    def search_update(self) -> UpdatePackage:
        """
        Getting response by url and verify using version parser to check for the correct version.

        Returns:
            Latest update package is available via the URL.
        """
        response = requests.get(self._toml_url, timeout=40, verify=self._verify)
        update_package = self.version_parser.get_latest_version_from_response(response)
        return update_package

    def need_to_update(self, latest_version: Union[str, None]) -> bool:
        """
        Checks if the latest version is available.

        Args:
            latest_version(Union[str, None]): latest version to check

        Returns:
            bool: True if the latest version is more than the current version, False otherwise
        """
        if latest_version is None:
            return False
        return Version(latest_version) > Version(self._version)

    def start_installer(self) -> UpdaterStatus:
        """
        Start update installer process
        """
        installer_path = get_update_installer_path()
        result = run_execute(installer_path, [self._download_latest_version_url])
        if result != 42:
            message = create_message_dict(
                UpdaterStatus.EXITED.value, 'Not accepted UAC'
            )

            self.delegate_mapping[UpdaterStatus.EXITED.value](message)
            return UpdaterStatus.EXITED
        else:
            message = create_message_dict(
                UpdaterStatus.STARTING.value,
                'Update launch completed successfully',
            )
            self.delegate_mapping[UpdaterStatus.STARTING.value](message)
            return UpdaterStatus.STARTING

    def listening_update_installer(self) -> UpdaterStatus:
        """
        Getting status from pipe channel and fulfilling delegate func by status
        """
        with self._named_pipe as channel:
            while True:
                time.sleep(1)
                message = channel.get_pipe_message()
                self.delegate_mapping[message['type']](message)
                if message['type'] == UpdaterStatus.PROCESSING:
                    status = UpdaterStatus.PROCESSING
                    continue
                elif message['type'] == UpdaterStatus.STARTING.value:
                    status = UpdaterStatus.STARTING
                    continue
                elif message['type'] == UpdaterStatus.EXITED.value:
                    status = UpdaterStatus.EXITED
                    break
                elif message['type'] == UpdaterStatus.NOT_FOUND.value:
                    status = UpdaterStatus.NOT_FOUND
                    break
                elif message['type'] == UpdaterStatus.ERROR.value:
                    status = UpdaterStatus.ERROR
                    break
                elif message['type'] == UpdaterStatus.FINISHED.value:
                    status = UpdaterStatus.FINISHED
                    break
        return status
