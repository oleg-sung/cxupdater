import json
from typing import Callable, Union, Any

import pywintypes
import win32file
import win32pipe

from cxupdater.config import UpdaterStatus
from cxupdater.utils import create_message_dict


class PipeReceiver:
    """
    Class for receiving messages from a named pipe channel.
    """
    def __init__(self, pipe_name: str) -> None:
        self.pipe_channel = self.__create_named_pipe(pipe_name)

    @staticmethod
    def __create_named_pipe(name: str) -> Union[Any, None]:
        """
        Create a named pipe channel.

        Args:
            name (str): The name of the pipe channel.

        Returns:
            Union[Any, None]: Returns the named pipe channel if created successfully, None otherwise.
        """
        try:
            pipe = win32pipe.CreateNamedPipe(
                rf'\\.\pipe\{name}',
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                1, 65536, 65536,
                0,
                None)
        except pywintypes.error:
            return
        return pipe

    def get_pipe_message(self) -> dict:
        _, data = win32file.ReadFile(self.pipe_channel, 4096)
        message = json.loads(data.decode('utf-8').strip())
        return message

    def __enter__(self):
        if not self.pipe_channel:
            raise RuntimeError('Cannot connect to an uninitialized pipe channel.')
        try:
            win32pipe.ConnectNamedPipe(self.pipe_channel, None)
        except pywintypes.error:
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        if self.pipe_channel:
            win32file.CloseHandle(self.pipe_channel)
            self.pipe_channel = None


class PipeWriter:
    """
    Class for writing message to pipe channel.
    """
    def __init__(self, pipe_name: str) -> None:
        self.handle = self.__connection_to_pipe_channel(pipe_name)

    @staticmethod
    def __connection_to_pipe_channel(name: str) -> Any:
        handle = win32file.CreateFile(
            rf'\\.\pipe\{name}',
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None)
        return handle

    def write_message(self, message: dict) -> None:
        """
        Write message encodes in UTF-8 to pipe channel.

        Args:
            message (dict): message in dict format
        """
        message_ = json.dumps(message).encode('utf-8')
        win32file.WriteFile(self.handle, message_)


class UpdateInstallerMessageHandler:
    """
    Class for handling update installer
    """

    def __init__(self, write_func: Callable[[dict], None], func_name: str) -> None:
        self.func_name = func_name
        self.write_func = write_func

    def __enter__(self):
        message = create_message_dict(
            UpdaterStatus.PROCESSING.value, f'{self.func_name} is in processing'
        )
        self.write_func(message)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None and exc_val is None and exc_tb is None:
            return True
        else:
            message = create_message_dict(
                UpdaterStatus.ERROR.value, f'Error during {self.func_name}',
                error=exc_type.__name__, error_message=str(exc_val)
            )
            self.write_func(message)
            raise
