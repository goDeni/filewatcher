import os
import socket as socket_
from json import dumps

from logging import getLogger

from filewatcher import commands

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
            conn, add = self.socket.accept()
            try:
                self.get_connection(conn)
            except Exception:
                log.exception("Error")
            conn.close()

    def get_connection(self, conn: socket_.socket):
        command = conn.recv(1024).decode('utf-8')
        res = None
        if commands.is_show_folder(command):
            res = self.show_folder()

        if not res:
            return

        conn.send(dumps({
            'response': res
        }).encode('utf-8'))

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
