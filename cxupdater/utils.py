import ctypes
import importlib.resources
import sys
from pathlib import Path
from urllib.parse import urlparse

from cxupdater.config import UPDATER_NAME


def get_update_installer_path():
    """
    Getting current update installer path.
    """
    update_installer_name = Path(sys.executable).name[:-4] + UPDATER_NAME + '.exe'
    return Path(sys.executable).parent / update_installer_name


def run_execute(path_to_exe: Path, args: list) -> int:
    """
    Run executable.

    Args:
        path_to_exe(Path): path to executable for starting
        args(list): list of arguments for executable

    Returns:
        int: integer status code of the result execution
    """
    return ctypes.windll.shell32.ShellExecuteW(
        None, "runas", str(path_to_exe), " ".join(args), None, 1
    )


def create_message_dict(type_: str, message_: str, **kwargs) -> dict:
    """
    Create message dictionary with necessary and additional fields.

    Args:
        type_ (str): type of message(one out of UpdaterStatus)
        message_ (str): message
        kwargs (str): additional fields

    Returns:
        dict: dictionary with necessary and additional fields. For example:
        {
            'type': 'STARTING',
            'message': 'Update launch completed successfully',
        }
        or
        {
            'type': 'Not Found',
            'message': 'Update not found',
            'url': 'https://example.com',
        }
    """
    return dict(type=type_, message=message_, **kwargs)


def get_script_path(script_name: str) -> str:
    """
    Retrieves the file system path of a script located in the 'cxupdater.scripts' package.

    This function uses the `importlib.resources.path` method to locate the script file
    in the specified package. If the script is not found, it raises a FileNotFoundError.

    Args:
        script_name (str): The name of the script file to locate (e.g., 'update_installer.py').

    Returns:
        str: The absolute file system path of the specified script.

    Raises:
        FileNotFoundError: If the specified script cannot be found in the package.
    """
    try:
        with importlib.resources.path('cxupdater.scripts', script_name) as path:
            return str(path)
    except Exception:
        raise FileNotFoundError(f"{script_name} is not found.")


def is_valid_url(url: str) -> bool:
    """
    Checks if the url is valid.

    Args:
        url (str): url to check

    Return:
        bool: True if url is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
