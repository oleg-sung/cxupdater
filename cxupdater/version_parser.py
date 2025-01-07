from typing import Dict, Tuple, Union

import toml
from requests import Response

from cxupdater.config import UpdatePackage, is_64bit


class VersionParser:

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
