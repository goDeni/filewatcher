import os
import socket as socket_
from json import loads, dumps
from getpass import getpass
from logging import getLogger

from filewatcher.commands import Commands
from filewatcher.utils import (
    download_file,
    download_folder,
    SIZE_POCKET,
    send_file,
    send_folder,
    get_files,
    get_folders,
    read_data,
)

log = getLogger(__name__)


def reopen_client(fun):
    def wrapper(self, *args, **kwargs):
        if self.is_close:
            self.connect()
        res = fun(self, *args, **kwargs)
        self.close()
        return res
    return wrapper


class ClientCommand:
    socket = socket_.socket()

    def __init__(self, host, port, password):
        self.is_close = False
        self.host = host
        self.port = port
        self.password = password

        self.connect()

    def connect(self):
        self.socket = socket_.socket()
        self.socket.settimeout(5)
        self.socket.connect((self.host, self.port))
        self.is_close = False

    def close(self):
        self.socket.close()
        self.is_close = True

    def send_command(self, command: str, args=None, wait_res=True, timeout=0, close_conn=True) -> dict:
        if self.is_close:
            self.connect()

        if timeout:
            self.socket.settimeout(timeout)
        self.socket.send(dumps({
            'command': command,
            'args': args,
            'hash': self.password,
        }).encode('utf-8'))
        if wait_res:
            response = read_data(self.socket)
            if close_conn:
                self.close()
            return loads(response)
        if close_conn:
            self.close()

    def show_folder(self, folder: str) -> tuple:
        response = self.send_command(Commands.SHOW_FOLDER.name, folder)
        return response.get('response'), response.get('err')

    @reopen_client
    def download(self, path_from: str, path_to: str) -> dict:
        self.send_command(Commands.DOWNLOAD.name, path_from, close_conn=False, wait_res=False)
        response = None

        res = loads(read_data(self.socket))

        if res.get('isfile'):
            filename, size = res.get('filename'), res.get('size')
            download_file(self.socket, size, os.path.join(path_to, filename))
        elif res.get('isfolder'):
            foldername, path, count_files = res.get('foldername'), res.get('path'), int(res.get('count_files'))
            download_folder(self.socket, os.path.join(path_to, foldername), count_files)
        else:
            response = {'err': ("Unknown response '{}'".format(res) if not res.get('err') else res.get('err'))}

        if not response:
            response = loads(self.socket.recv(SIZE_POCKET).decode('utf-8'))

        return response

    @reopen_client
    def upload(self, path_source: str, path_dist: str) -> dict:
        res = None
        path, name = os.path.split(path_source)
        if os.path.isfile(path_source):
            res = send_file(self.socket, path_source, name, path_dist, this_command=True, kwargs={
                'command': Commands.UPLOAD.name,
                'hash': self.password,
            })
        elif os.path.isdir(path_source):
            res = send_folder(self.socket, ('', path_source), name, path_dist, this_command=True, kwargs={
                'command': Commands.UPLOAD.name,
                'hash': self.password,
            })
        else:
            log.warning("Path %s not found", path_source)
            return {'response': 0, 'err': "Path {} not found".format(path_source)}
        if isinstance(res, dict):
            return res

        res = self.socket.recv(SIZE_POCKET).decode('utf-8')
        res = loads(res)
        return res

    @reopen_client
    def delete(self, delete_obj: str) -> dict:
        return self.send_command(Commands.DELETE.name, delete_obj)

    def login(self):
        password = getpass("Enter password: ")
        return self.send_command(Commands.LOGIN.name, password, timeout=60)['response']

    @reopen_client
    def check_tree(self, path: str):
        three_files = list(get_files(path, is_root=True, get_size=True))
        three_folders = list(get_folders(path, is_root=True))
        return self.send_command(Commands.CHECK_THREE.name, {'files': three_files, 'folders': three_folders})

    def rename(self, rename_d: list) -> dict:
        return self.send_command(Commands.RENAME.name, rename_d)

    def move(self, move_d: list) -> dict:
        return self.send_command(Commands.MOVE.name, move_d)

    def copy(self, copy_d: list) -> dict:
        return self.send_command(Commands.COPY.name, copy_d)
