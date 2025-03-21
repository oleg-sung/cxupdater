import os
import re
import subprocess
import sys
from pathlib import Path

from packaging.version import Version


VERSION_PATTERN = r'\d+\.\d+(?:\.\d+)*'
PREFIX = 'win-amd64' if sys.maxsize > 2**32 else 'win32'


def get_latest_exe_path_from_local_folder(src: Path, app_name: str) -> Path:
    """
    Getting a path of the latest version from src path using name of the app.

    Args:
        src (Path): Path of the source folder.
        app_name (str): Name of the app.

    Returns:
        Path of the latest app executable.
    """
    found_package_names = [
        (fname, re.search(VERSION_PATTERN, fname).group())
        for fname in os.listdir(src)
        if fname.startswith(app_name) and fname.endswith(PREFIX) and re.search(VERSION_PATTERN, fname)
    ]
    latest_version = max(found_package_names, key=lambda x: Version(x[1]))
    execute_name = app_name + '.exe'
    return src / latest_version[0] / execute_name


def main(path: Path):
    args = sys.argv[1:]
    command = [str(path)] + args
    process = subprocess.Popen(command, cwd=path.parent)
    if any(args):
        process.wait()
    else:
        pass


if __name__ == "__main__":
    path_to_executable = Path(sys.executable)
    src_folder_path = path_to_executable.parent
    name = path_to_executable.name
    main_exe_path = get_latest_exe_path_from_local_folder(src_folder_path, name[:-4])
    main(main_exe_path)
    sys.exit(0)
