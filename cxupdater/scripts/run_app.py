import subprocess
import sys
from pathlib import Path

from cxupdater import VersionParser


def main(path: Path):
    args = sys.argv[1:]
    command = [str(path)] + args
    process = subprocess.Popen(command)
    if any(args):
        process.wait()
    else:
        pass


if __name__ == "__main__":
    parser = VersionParser()
    path_to_executable = Path(sys.executable)
    src_folder_path = path_to_executable.parent
    name = path_to_executable.name
    main_exe_path = parser.get_latest_exe_path_from_local_folder(src_folder_path, name[:-4])
    main(main_exe_path)
    sys.exit(0)
