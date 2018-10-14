import os
import socket as socket_
from json import dumps, loads

from logging import getLogger

from filewatcher.commands import Commands
from filewatcher.utils import check_password

log = getLogger(__name__)


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size


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
        log.warning(data)
        data = loads(data)
        hash_ = data['hash']
        log.warning("hash %s", hash_)
        log.warning("pass %s", self.password)
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
        if command == Commands.SHOW_FOLDER.name:
            res = self.show_folder()
        elif command == Commands.LOGIN.name:
            res = self.login(args)

        if res is None:
            return
        return dumps({
            'response': res
        }).encode('utf-8')

    def show_folder(self) -> list:
        directory = []
        for dir_name in os.listdir(self.directory):
            path = os.path.join(self.directory, dir_name)
            log.warning(path)
            if os.path.isdir(path):
                directory.append([
                    "FOLDER",
                    dir_name,
                    get_size(path),
                    os.path.getmtime(path),
                ])
            elif os.path.isfile(path):
                directory.append([
                    "FILE",
                    dir_name,
                    os.path.getsize(path),
                    os.path.getmtime(path)
                ])
        return directory

    def close(self):
        self.socket.close()
