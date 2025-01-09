# cxupdater

The library for making updates package and the auto-update based on cx_Freeze.

## Installation
Install the current version with PyPI:
```bash
pip install cxupdater
```
Or from Github:
```bash
pip install https://github.com/oleg-sung/cxupdater/archive/main.zip
```

## Usage
1. Create the update package using Executable from cx_Freeze and setup from cxupdater:
   ```python
    from cxupdater import setup
    from cx_Freeze import Executable
    
    
    windows = Executable(
        'test.py',
        target_name='TestApp',
        icon='some_icon.ico'
    )
   
    setup(
        name='TestApp',
        version='1.0.1',
        options={
           'build_update': {
               "optimize": 2,
            }
        },
        executables=[windows]
        )
   ```
   Use **build_update** command with setup. The command **build_update** supports the same params **build_exe** from cx_Freeze.
   ```
   python setup.py build_update
   ```
   During the execution of the command, a zip archive will be created containing an intermediate executable file for launching the main application and Updater.exe to update the application automatically.
2. Use the `generate_toml -p path\to\folder\contains\update\packages -u https://example.com(your ftp update server)` command or create a .toml with the same name as the application, for example TestApp.toml with the following contents:
   ```toml
   [cxupdater.package.x32] # or x64 

   name = "TestApp-1.0.0.win32"  
   version = "1.0.1"
   url = "https://example/TestApp-1.0.1.win32.zip"

   ```
   Where there are:
      * **name**: The name includes an app's name, version and arch prefix.
      * **version**: Version of the app
      * **url**: The url for downloading update package
3. Move TestApp.toml and TestApp-1.0.0.win32.zip to https://example/ (your ftp server for publishing an updates)
4. In the code application, create an instance of the update by providing the URL to the file.toml, the current version of the application, implements the delegate of the CxDelegateInterface interface.
   ```python
   from cxupdater import CxUpdater, CxDelegateInterface
   
   
   class Delegate(CxDelegateInterface):
   
        def do_processing_update(self, message: dict) -> None:
            pass
   
        def do_not_found_update(self, message: dict) -> None:
            pass
   
        def do_error_update(self, message: dict) -> None:
            pass
   
        def do_exited_update(self, message: dict) -> None:
            pass
   
        def do_finished_update(self, message: dict) -> None:
            pass
   
        def do_start_update(self, message: dict) -> None:
            pass
   
   delegate = Delegate()
   updater = CxUpdater('https://example/TestApp.toml', '1.0.0', delegate)
   updater.do_auto_updater()
   ```
   the do_auto_updater() method starts the process of searching for updates. If an update has been found, run Updater.exe with a UAC request and the transmission of the url for downloading and installing the update package. After that, the **Updater** will inform us about the update progress using delegate methods.
   If no update was found, do_auto_updater() returns the status **Not found**.

## Contributing

Bug reports and/or pull requests are welcome


## License

The module is available as open source under the terms of the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0)
