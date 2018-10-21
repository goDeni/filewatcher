import os
import socket as socket_
from json import dumps, loads
from logging import getLogger

from filewatcher.utils import (
    get_three,
    get_count_files,
    get_files,
)
SIZE_POCKET = 1024

log = getLogger(__name__)


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
        'three': get_three(download_path[0], download_path[1]),
        'count_files': get_count_files(os.path.join(download_path[0], download_path[1])),
    }
    if this_command and isinstance(kwargs, dict):
        folder_info = {'args': folder_info, **kwargs}

    socket.send(dumps(folder_info).encode('utf-8'))
    res = socket.recv(SIZE_POCKET).decode('utf-8')
    if not res:
        return "Success flag didn't receive"
    download_path = os.path.join(download_path[0], download_path[1])
    for file in get_files(download_path):
        path_f, filename = os.path.split(file[len(download_path)+1:])
        send_file(socket, file, filename, path_f)

    return 1


def download_file(socket: socket_.socket, size: int, download_path: str):
    print("Downloading", download_path)
    log.warning("Download path %s, size %s", download_path, size)
    with open(download_path, 'wb') as file_:
        socket.send('1'.encode('utf-8'))
        downloaded_data = 0
        pocket_size = SIZE_POCKET
        while size:
            data = socket.recv(min(pocket_size, size))
            size -= len(data)
            downloaded_data += len(data)
            file_.write(data)


def download_folder(socket: socket_.socket, three: list, download_path: str, count_files: int):
    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    path, download_folder = os.path.split(download_path)
    for path_d in three:
        if not os.path.isdir(os.path.join(path, path_d)):
            os.makedirs(os.path.join(path, path_d))
    socket.send('1'.encode('utf-8'))
    while count_files:
        file_info = loads(socket.recv(SIZE_POCKET).decode('utf-8'))
        size, path, filename = file_info.get('size'), file_info.get('path'), file_info.get('filename')
        if None in [size, path, filename]:
            print("Download error", file_info)
            log.error("Download error %s", file_info)
        else:
            download_file(socket, size, os.path.join(download_path, path, filename))
        count_files -= 1
