import os
import socket as socket_
from json import loads, dumps
from getpass import getpass

from filewatcher.commands import Commands, SIZE_POCKET


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
            response = self.socket.recv(SIZE_POCKET)
            # print(response, command, args)
            if close_conn:
                self.close()
            return loads(response.decode('utf-8'))
        if close_conn:
            self.close()

    def show_folder(self, folder: str) -> tuple:
        response = self.send_command(Commands.SHOW_FOLDER.name, folder)
        return response.get('response'), response.get('err')

    def download(self, path_from: str, path_to: str) -> dict:
        self.send_command(Commands.DOWNLOAD.name, path_from, close_conn=False, wait_res=False)
        response = None

        res = loads(self.socket.recv(10240).decode('utf-8'))

        if res.get('isfile'):
            filename, size = res.get('filename'), res.get('size')
            download_file(self.socket, size, os.path.join(path_to, filename))
        elif res.get('isfolder'):
            three, foldername, path, count_files = res.get('three'), res.get('foldername'), res.get('path'), int(res.get('count_files'))
            download_folder(self.socket, three, os.path.join(path_to, foldername), count_files)
        else:
            response = {'err': ("Unknown response '{}'".format(res) if not res.get('err') else res.get('err'))}

        if not response:
            response = loads(self.socket.recv(1024).decode('utf-8'))

        self.close()
        return response

    def upload(self):
        pass

    def login(self):
        password = getpass("Enter password: ")
        return self.send_command(Commands.LOGIN.name, password, timeout=60)['response']


def download_file(socket: socket_.socket, size, download_path):
    print("Downloading", download_path)
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
        file_info = loads(socket.recv(1024).decode('utf-8'))
        size, path, filename = file_info.get('size'), file_info.get('path'), file_info.get('filename')
        if None in [size, path, filename]:
            print("Download error", file_info)
        else:
            download_file(socket, size, os.path.join(download_path, path, filename))
        count_files -= 1
