import os
import re
from pathlib import Path
from typing import Dict, Tuple, Union, List

import toml
from requests import Response

from cxupdater.config import UpdatePackage, is_64bit


class PackageParser:

    PACKAGE_PATTERN = r"^(?P<name>[A-Za-z0-9_-]+)-(?P<version>\d+(\.\d+)*?)\.(?P<arch>win(?:-amd64|32))\.zip$"

    def __init__(self):
        pass

    def get_latest_version_from_response(self, response: Response) -> UpdatePackage:
        """
        Getting the latest version from response and return the maximum available version.

        Args:
            response (Response): response from sftp server

        Returns:
            UpdatePackage includes the max available version
        """
        try:
            parsed_data = toml.loads(response.text)
        except toml.TomlDecodeError:
            return UpdatePackage('0')
        if parsed_data is not None:
            result = self._toml_parser(parsed_data)
            if result is not None:
                name, url, version = result
                return UpdatePackage(version, name=name, address=url)

        return UpdatePackage('0')

    @staticmethod
    def _toml_parser(toml_dict: Dict) -> Union[Tuple[str, str, str], None]:
        """
        Pars toml config dict to return defined values from toml dict.

        Args:
            toml_dict (Dict): dict of toml config

        Returns:
            If there is an arh key(x32 or x64) in toml config then return url, version and name in string format.
            if there is not an arh key then return None.
        """
        arh = 'x64' if is_64bit() else 'x32'
        package_data = toml_dict['cxupdater']['package'].get(arh, None)
        if package_data is None:
            return None
        else:
            name = package_data.get('name', None)
            version = package_data.get('version', None)
            url = package_data.get('url', None)
            return name, url, version

    def get_list_packages_from_local_folder(self, path: Path) -> List[UpdatePackage]:
        """
        Getting the list of packages from local folder.

        Args:
            path (Path): path to local folder containing packages

        Return:
            List of updated packages
        """
        result = []
        for f_name in os.listdir(path):
            match = re.match(self.PACKAGE_PATTERN, f_name)
            if match is not None:
                name = match.group('name')
                version = match.group('version')
                arch = match.group("arch")
                result.append(UpdatePackage(version, name=name, arch=arch))

        return result

    @staticmethod
    def get_latest_version_by_arch(packages_list: List[UpdatePackage], arch: str) -> Union[UpdatePackage, None]:
        """
        Getting the latest version from list of packages by the architecture (win32 or win-amd64)

        Args:
            packages_list (List[UpdatePackage]): list of updated packages
            arch (str): package architecture for searching (win32 or win-amd64)

        Return:
            UpdatePackage includes the max available version or None if there is no available version.
        """
        packages = list(filter(lambda x: x.arch == arch, packages_list))

        return max(packages) if any(packages) else None
