#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from typing import Union
from urllib.parse import urljoin

import toml

from cxupdater import PackageParser
from cxupdater.config import UpdatePackage
from cxupdater.utils import is_valid_url


def crate_toml_dict(
        url_: str,
        latest_package: Union[UpdatePackage, None] = None,
) -> dict:
    """
    Create correct toml dict

    Args:
        url_ (str): the domain of a server for publishing an updates
        latest_package (Union[UpdatePackage, None]): Latest version of package
    Return:
        Toml dict for x32 version and x64 version if there are an available packages
    """

    data = {}
    if latest_package is not None:
        name = f'{latest_package.name}-{latest_package.version}.{latest_package.arch}'
        data['cxupdater'] = {
            'package': {
                'x32' if latest_package.arch == 'win32' else 'x64': {
                    'name': name,
                    'version': latest_package.version,
                    'url': urljoin(url_, name),
                }
            }
        }

    return data


def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description='Create toml file for update packages')
    parser.add_argument(
        '-p', '--path', type=str, nargs='?', required=True,
        help='path to folder contains update packages',
    )
    parser.add_argument(
        '-u', '--url', type=str, nargs='?', required=True,
        help='domain of your server for publishing updates',
    )
    args = parser.parse_args()
    path = Path(args.path)
    if not is_valid_url(args.url):
        sys.exit('Invalid url')
    url = args.url
    packages_parser = PackageParser()
    try:
        packages = packages_parser.get_list_packages_from_local_folder(path)
    except WindowsError:
        sys.exit(f'Invalid path: {path}')

    x32_latest_package = packages_parser.get_latest_version_by_arch(packages, 'win32')
    x64_latest_package = packages_parser.get_latest_version_by_arch(packages, 'win-amd64')
    if x32_latest_package is None and x64_latest_package is None:
        sys.exit(f'No updated packages found by path: {path}')
    else:
        if x32_latest_package is not None:
            file_name = f'{x32_latest_package.name}.toml'
        else:
            file_name = f'{x64_latest_package.name}.toml'

        x32_dict = crate_toml_dict(url, x32_latest_package)
        x64_dict = crate_toml_dict(url, x64_latest_package)
        x32_dict.update(x64_dict)
        with open(path / file_name, 'w', encoding='UTF-8') as file:
            toml.dump(x32_dict, file)
        print('Successfully created toml file')
