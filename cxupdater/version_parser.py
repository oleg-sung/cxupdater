import os
import re
from pathlib import Path
from typing import Dict, Tuple, Union

import toml
from packaging.version import Version
from requests import Response

from cxupdater.config import UpdatePackage, ARCH_PREFIX, is_64bit


class VersionParser:
    VERSION_PATTERN = r'\d+\.\d+(?:\.\d+)*'

    def __init__(self):
        pass

    def get_latest_exe_path_from_local_folder(self, src: Path, app_name: str) -> Path:
        """
        Getting a path of the latest version from src path using name of the app.

        Args:
            src (Path): Path of the source folder.
            app_name (str): Name of the app.

        Returns:
            Path of the latest app executable.
        """
        found_package_names = [
            UpdatePackage(name, None, re.search(self.VERSION_PATTERN, name).group())
            for name in os.listdir(src)
            if name.startswith(app_name) and name.endswith(ARCH_PREFIX) and re.search(self.VERSION_PATTERN, name)
        ]
        latest_version = max(found_package_names, key=lambda x: Version(x.version))
        execute_name = app_name + '.exe'
        return src / latest_version.name / execute_name

    def get_latest_version_from_response(self, response: Response) -> UpdatePackage:
        """
        Getting the latest version from response and return the maximum available version.

        Args:
            response (Response): response from sftp server

        Returns:
            UpdatePackage includes the max available version
        """
        parsed_data = toml.loads(response.text)
        if parsed_data is not None:
            name, url, version = self._toml_parser(parsed_data)
            return UpdatePackage(name=name, address=url, version=version)

        else:
            return UpdatePackage(None, None, '0')

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
