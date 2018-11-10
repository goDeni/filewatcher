import os
import socket as socket_
import shutil

from json import dumps, loads

from logging import getLogger

from filewatcher.commands import Commands
from filewatcher.utils import (
    check_password,
    get_folder_size,
    send_folder,
    send_file,
    download_file,
    download_folder,
    get_files,
    read_data,
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
        log.warning("Start listening on {}:{}".format(self.host, self.port))
        while True:
            self.connection, add = self.socket.accept()
            self.connection.settimeout(10)
            try:
                self.connection.send(self.get_connection())
            except Exception:
                log.exception("Error")
            self.connection.close()

    def get_command(self):
        data = read_data(self.connection)
        log.debug("data: %s", data)
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
        log.debug("%s %s", command, args)
        res = None
        error = None
        if command == Commands.SHOW_FOLDER.name:
            res, error = self.show_folder(args)
        elif command == Commands.LOGIN.name:
            res = self.login(args)
        elif command == Commands.DOWNLOAD.name:
            res, error = self.download(args)
        elif command == Commands.UPLOAD.name:
            res, error = self.upload(args)
        elif command == Commands.DELETE.name:
            res, error = self.delete(args)
        elif command == Commands.CHECK_THREE.name:
            res, error = self.check_three(args)
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

    def upload(self, path_info: dict):
        if path_info.get('isfile'):
            size, path, filename = path_info.get('size'), path_info.get('path'), path_info.get('filename')
            if not os.path.isdir(os.path.join(self.directory, path)):
                return None, "Invalid path {}".format(path)
            download_file(self.connection, size, os.path.join(self.directory, path, filename))
            return 1, None
        elif path_info.get('isfolder'):
            foldername, path, count_files = path_info.get('foldername'), path_info.get('path'), path_info.get('count_files')
            if path == '.':
                path = ''

            download_folder(self.connection, os.path.join(self.directory, path, foldername), count_files)
            return 1, None
        return None, "Invalid path info {}".format(path_info)

    def delete(self, delete_dir: str):
        if not delete_dir or delete_dir.startswith('/'):
            return 0, "Invalid path"

        delete_dir = os.path.join(self.directory, delete_dir)
        if os.path.isfile(delete_dir):
            os.remove(delete_dir)
        elif os.path.isdir(delete_dir):
            shutil.rmtree(delete_dir)
        else:
            return 0, "Invalid path"
        return 1, None

    def check_three(self, three: list):
        this_three = list(get_files(self.directory, is_root=True, get_size=True))

        delete_dirs = [d[0] for d in this_three if d not in three]
        need_dirs = [d[0] for d in three if d not in this_three]

        for directory in delete_dirs:
            directory = os.path.join(self.directory, directory)
            if os.path.isfile(directory):
                os.remove(directory)
        return need_dirs, None
