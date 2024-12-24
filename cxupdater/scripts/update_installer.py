import os
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests

from cxupdater.pipe_connecter import PipeWriter, UpdateInstallerMessageHandler
from cxupdater.config import NAMED_PIPE, ARCH_PREFIX, UpdaterStatus
from cxupdater.utils import create_message_dict


class UpdateInstaller:
    DESKTOP_FOLDER = Path(sys.executable).parent.parent
    UPDATE_FOLDER = DESKTOP_FOLDER / 'updates'
    TEMP_FOLDER = UPDATE_FOLDER / 'temp'
    DOWNLOAD_FOLDER = UPDATE_FOLDER / 'downloads'

    def __init__(self, url: str):
        self.url = url
        self.zip_name = Path(urlparse(self.url).path).name
        self.zip_path = None
        self.pipe_channel = PipeWriter(NAMED_PIPE)
        self.arh = ARCH_PREFIX
        self.pipe_error_handler = UpdateInstallerMessageHandler

    def install_updates(self) -> None:
        self.cleanup()

        self.download_updates()

        self.extract_zip(self.zip_path, self.TEMP_FOLDER)

        self.move_item(self.arh)

        self.remove_old_lib()

        self.move_item('lib')

        self.cleanup()
        message = create_message_dict(
            UpdaterStatus.FINISHED.value, 'Finished installing updates',
        )
        self.pipe_channel.write_message(message)

    def extract_zip(self, zip_path: str, destination: Path) -> None:
        """
        Extract content of a zip archive to a folder.

        Args:
            zip_path (str): The path to the zip archive.
            destination (Path): The path to the folder to extract the archive to.
        """
        with self.pipe_error_handler(self.pipe_channel.write_message, self.extract_zip.__name__):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                destination.mkdir(exist_ok=True)
                zip_ref.extractall(destination)

    def download_updates(self) -> None:
        """
        Download the latest version of the updates using the URL obtained from sys args.
        """
        with self.pipe_error_handler(self.pipe_channel.write_message, self.download_updates.__name__):
            r = requests.get(self.url, stream=True, verify=False)
            r.raise_for_status()
            self.UPDATE_FOLDER.mkdir(parents=True, exist_ok=True)
            self.DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            self.zip_path = self.DOWNLOAD_FOLDER / self.zip_name
            with open(self.zip_path, 'wb') as file:
                for chunk in r.iter_content(chunk_size=128000):
                    if chunk:
                        file.write(chunk)

    def move_item(self, pattern: str) -> None:
        """
        Move a file/folder from TEMP_FOLDER to DESKTOP_FOLDER

        Args:
            pattern (str): Ending pattern for the file/folder name to be moved.
        """
        with self.pipe_error_handler(self.pipe_channel.write_message, self.move_item.__name__):
            for path in os.listdir(self.TEMP_FOLDER):
                if path.endswith(pattern):
                    path = self.TEMP_FOLDER / path
                    shutil.move(str(path), str(self.DESKTOP_FOLDER))

    def remove_old_lib(self) -> None:
        """
        Removed old lib in the DESKTOP FOLDER
        """
        with self.pipe_error_handler(self.pipe_channel.write_message, self.remove_old_lib.__name__):
            for path in os.listdir(self.DESKTOP_FOLDER):
                if path == 'lib':
                    path = self.DESKTOP_FOLDER / path
                    if path.is_dir():
                        shutil.rmtree(str(path))

    def cleanup(self) -> None:
        """
        General clean up UPDATE FOLDER
        """
        try:
            shutil.rmtree(str(self.UPDATE_FOLDER))
        except WindowsError:
            pass


if __name__ == '__main__':
    try:
        downloaded_url = sys.argv[1]
        updater = UpdateInstaller(downloaded_url)
        updater.install_updates()
    except:
        pass
    sys.exit(0)
