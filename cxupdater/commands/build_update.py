import os
import shutil
import zipfile
from pathlib import Path

from cx_Freeze import Executable
from cx_Freeze.command.build_exe import BuildEXE

from cxupdater.config import UPDATER_NAME, ARCH_PREFIX
from cxupdater.utils import get_script_path


class BuildUpdate(BuildEXE):

    def initialize_options(self):
        if hasattr(self.distribution, 'executables'):
            main_executable: Executable = self.distribution.executables[0]
            self.distribution.get_version()
            self.app_icon = main_executable.icon
            self.app_name = main_executable.target_name[:-4]
            updater = Executable(
                get_script_path('update_installer.py'),
                target_name=self.app_name + UPDATER_NAME,
                icon=self.app_icon,
                base='Win32GUI',
            )
            self.distribution.executables.append(updater)
            super().initialize_options()
            self.pref = ARCH_PREFIX
            self.build_exe = f'build/{self.app_name}-{self.distribution.get_version()}.{self.pref}'

    def run(self):
        super().run()
        self._create_build_exe_distribution()
        update_package = f'{self.app_name}-{self.distribution.get_version()}.{self.pref}'
        super().run()
        shutil.copytree('build/' + update_package, 'build/' + self.app_name + os.sep + update_package)
        self.make_zip_archive(Path('build') / self.app_name, update_package)

    def make_zip_archive(self, src: Path, title: str) -> None:
        """
        Args:
            src(Path): folder path from which zip archive will be created
            title(str): title of the zip archive
        """
        path = Path('build') / (title + '.zip')
        zip_path = path.parent / (title + '.zip')

        with zipfile.ZipFile(zip_path, 'w') as archive:
            for file_path in src.rglob('*'):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(src))
        self.remove_non_zip_files(Path('build'))

    @staticmethod
    def remove_non_zip_files(folder_path: Path) -> None:
        """
        Remove all files and folders from folder expect .zip file

        Args:
            folder_path(Path): folder path from which needs to removed non zip files
        """
        for item in os.listdir(folder_path.absolute()):
            item_path = folder_path / item
            try:
                if item_path.is_file() and not item.endswith('.zip'):
                    os.remove(item_path)

                elif item_path.is_dir():
                    shutil.rmtree(item_path)
            except OSError:
                pass

    def _create_build_exe_distribution(self) -> None:
        """
        Change current distribution to create a separate executable file
        for starting latest version in local folder
        """
        self._clean_up_distribution()
        self.build_exe = 'build/' + self.app_name
        executable = Executable(
            get_script_path('run_app.py'),
            target_name=self.app_name,
            icon=self.app_icon,
            base='Win32GUI',
        )
        self.distribution.command_options['build_exe'] = {'build_exe': ('setup script', self.build_exe)}
        self.distribution.executables = [executable]
        self.distribution.commands = ['build_exe']

    def _clean_up_distribution(self) -> None:
        """
        Clean up current distribution from old options and data files.
        Delete build_update key from distribution's command options
        """
        if self.distribution.command_options.get('build_update', False):
            del self.distribution.command_options['build_update']
        for option in self.list_options:
            setattr(self, option, [])
        self.distribution.data_files = []
