import os
import socket as socket_
from json import dumps, loads

from logging import getLogger

from filewatcher.commands import Commands, SIZE_POCKET
from filewatcher.utils import (
    check_password,
    get_folder_size,
    get_three,
    get_count_files,
    get_files,
)

log = getLogger(__name__)


class ServerFwr:
    socket = socket_.socket()
    connection = socket_.socket()

    def __init__(self, host, port, password, directory):
        self.host = host
        self.port = port
        self.socket.bind((host, port))
        self.socket.listen(10)
        self.password = password
        self.directory = directory

    def listen(self):
        log.info("Start listening on {}:{}".format(self.host, self.port))
        while True:
            self.connection, add = self.socket.accept()
            try:
                self.connection.send(self.get_connection())
            except Exception:
                log.exception("Error")
            self.connection.close()

    def get_command(self):
        data = self.connection.recv(1024).decode('utf-8')
        data = loads(data)
        hash_ = data['hash']
        if hash_ == self.password or data['command'] == Commands.LOGIN.name:
            return data['command'], data['args']
        return None, None

    def login(self, password: str) -> [str, False]:
        if check_password(password, self.password):
            return self.password
        return False

    def get_connection(self):
        command, args = self.get_command()
        if command is None and args is None:
            return dumps({
                'err': 'Invalid password'
            }).encode('utf-8')
        res = None
        error = None
        if command == Commands.SHOW_FOLDER.name:
            res, error = self.show_folder(args)
        elif command == Commands.LOGIN.name:
            res = self.login(args)
        elif command == Commands.DOWNLOAD.name:
            res, error = self.download(args)

        if res is None and error is None:
            return
        return dumps({
            'response': res,
            'err': error
        }).encode('utf-8')

    def show_folder(self, folder) -> tuple:
        directory = {'files': [], 'folders': []}

        path_directory = self.directory
        if folder != '.':
            path_directory = os.path.join(path_directory, folder)

        if not os.path.isdir(path_directory):
            return None, "Invalid path /{}".format(folder)

        for dir_name in os.listdir(path_directory):
            path = os.path.join(path_directory, dir_name)
            if os.path.isdir(path):
                directory['folders'].append([
                    dir_name,
                    get_folder_size(path),
                    os.path.getmtime(path),
                ])
            elif os.path.isfile(path):
                directory['files'].append([
                    dir_name,
                    os.path.getsize(path),
                    os.path.getmtime(path)
                ])
        return directory, None

    def close(self):
        self.socket.close()

    def download(self, folder: str):
        error = None
        download_path = os.path.join(self.directory, folder)
        path, name = os.path.split(folder)
        if os.path.isfile(download_path):
            return send_file(self.connection,
                             download_path=download_path,
                             filename=name,
                             path=path), error
        elif os.path.isdir(download_path):
            return send_folder(self.connection,
                               download_path=(self.directory, folder),
                               foldername=name,
                               path=path), error
        else:
            return None, "Invalid path"


def send_file(socket: socket_.socket, download_path: str, filename: str, path=''):
    socket.send(dumps({
        'filename': filename,
        'path': path,
        'size': os.path.getsize(download_path),
        'isfile': True,
    }).encode('utf-8'))
    res = socket.recv(1024).decode('utf-8')
    if not res:
        return "Success flag didn't receive"
    with open(download_path, 'rb') as file_:
        data = file_.read(SIZE_POCKET)
        while data:
            socket.send(data)
            data = file_.read(SIZE_POCKET)

    return 1


def send_folder(socket: socket_.socket, download_path: tuple, foldername: str, path=''):
    socket.send(dumps({
        'foldername': foldername,
        'path': path,
        'isfolder': True,
        'three': get_three(download_path[0], download_path[1]),
        'count_files': get_count_files(os.path.join(download_path[0], download_path[1])),
    }).encode('utf-8'))

    res = socket.recv(1024).decode('utf-8')
    if not res:
        return "Success flag didn't receive"
    download_path = os.path.join(download_path[0], download_path[1])
    for file in get_files(download_path):
        path_f, filename = os.path.split(file[len(download_path)+1:])
        send_file(socket, file, filename, path_f)

    return 1
