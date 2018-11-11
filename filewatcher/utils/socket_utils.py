import os
import socket as socket_
from json import dumps, loads
from logging import getLogger

from filewatcher.utils import (
    get_count_files,
    get_files,
)
SIZE_POCKET = 1024
TIMEOUT = 10

log = getLogger(__name__)


def read_data(socket: socket_.socket) -> str:
    data = socket.recv(SIZE_POCKET)
    while data.startswith(b'{') and not data.endswith(b'}'):
        data += socket.recv(SIZE_POCKET)
    return data.decode('utf-8')


def send_file(socket: socket_.socket, download_path: str, filename: str, path='', this_command=False, kwargs=None):
    file_info = {
        'filename': filename,
        'path': path,
        'size': os.path.getsize(download_path),
        'isfile': True,
    }
    if this_command and isinstance(kwargs, dict):
        file_info = {'args': file_info, **kwargs}

    socket.send(dumps(file_info).encode('utf-8'))
    res = socket.recv(SIZE_POCKET).decode('utf-8')
    if not res:
        return "Success flag didn't receive"
    elif len(res) > 1:
        log.debug(res)
        return loads(res)

    with open(download_path, 'rb') as file_:
        data = file_.read(SIZE_POCKET)
        while data:
            socket.send(data)
            data = file_.read(SIZE_POCKET)

    return 1


def send_folder(socket: socket_.socket, download_path: tuple, foldername: str, path='', this_command=False, kwargs=None):
    folder_info = {
        'foldername': foldername,
        'path': path,
        'isfolder': True,
        'count_files': get_count_files(os.path.join(download_path[0], download_path[1])),
    }
    if this_command and isinstance(kwargs, dict):
        folder_info = {'args': folder_info, **kwargs}

    socket.send(dumps(folder_info).encode('utf-8'))
    res = socket.recv(SIZE_POCKET).decode('utf-8')

    if not res:
        return "Success flag didn't receive"
    elif len(res) > 1:
        return loads(res)

    download_path = os.path.join(download_path[0], download_path[1])
    for file in get_files(download_path):
        path_f, filename = os.path.split(file[len(download_path)+1:])
        send_file(socket, file, filename, path_f)

    return 1


def download_file(socket: socket_.socket, size: int, download_path: str):
    # print("Downloading", download_path)
    log.warning("Downloading %s", download_path)
    with open(download_path, 'wb') as file_:
        socket.send('1'.encode('utf-8'))
        downloaded_data = 0
        pocket_size = SIZE_POCKET
        while size:
            data = socket.recv(min(pocket_size, size))
            if not data:
                raise ConnectionError("Downloading file error")
            size -= len(data)
            downloaded_data += len(data)
            file_.write(data)


def download_folder(socket: socket_.socket, download_path: str, count_files: int):
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    elif not os.path.isdir(download_path):
        socket.send(dumps({
            'res': '',
            'err': 'Invalid path'
        }).encode('utf-8'))
        return 0

    if count_files:
        socket.send('1'.encode('utf-8'))
    while count_files:
        file_info = loads(socket.recv(SIZE_POCKET).decode('utf-8'))
        size, path, filename = file_info.get('size'), file_info.get('path'), file_info.get('filename')
        if None in [size, path, filename]:
            print("Download error", file_info)
            log.warning("Download error %s", file_info)
        else:
            path_tmp = os.path.join(download_path, path)
            if not os.path.isdir(path_tmp):
                os.makedirs(path_tmp)
            download_file(socket, size, os.path.join(path_tmp, filename))
        count_files -= 1
    return 1
