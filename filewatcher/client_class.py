import socket as socket_
from json import loads, dumps
from getpass import getpass

from filewatcher.commands import Commands, SIZE_POCKET


class ClientCommand:
    socket = socket_.socket()

    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

        self.connect()

    def connect(self):
        self.socket = socket_.socket()
        self.socket.settimeout(5)
        self.socket.connect((self.host, self.port))

    def send_command(self, command: str, args=None, wait_res=True) -> dict:
        self.socket.send(dumps({
            'command': command,
            'args': args,
            'hash': self.password,
        }).encode('utf-8'))
        if wait_res:
            response = self.socket.recv(SIZE_POCKET)
            # print(response, command, args)
            return loads(response.decode('utf-8'))

    def show_folder(self) -> tuple:
        response = self.send_command(Commands.SHOW_FOLDER.name)
        return response.get('response'), response.get('err')

    def download(self):
        pass

    def upload(self):
        pass

    def login(self):
        password = getpass("Enter password: ")
        return self.send_command(Commands.LOGIN.name, password)['response']

