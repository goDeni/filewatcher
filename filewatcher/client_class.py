import socket as socket_
from json import loads

from filewatcher import commands


class ClientCommand:
    socket = socket_.socket()

    def __init__(self, host, port, password):
        self.socket.connect((host, port))

    def send_command(self, command: str):
        self.socket.send(command.encode('utf-8'))
        response = self.socket.recv(commands.SIZE_POCKET)
        return loads(response.decode('utf-8'))

    def show_folder(self) -> list:
        return self.send_command(commands.SHOW_FOLDER)['response']

    def download(self):
        pass

    def upload(self):
        pass

    def connect(self):
        pass
