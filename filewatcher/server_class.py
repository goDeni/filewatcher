import socket as socket_

from logging import getLogger

log = getLogger(__name__)


class ServerFwr:
    socket = socket_.socket()

    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.socket.bind((host, port))
        self.socket.listen(10)
        self.password = password

    def listen(self):
        log.info("Start listening on {}:{}".format(self.host, self.port))
        while True:
            conn, add = self.socket.accept()
            print(conn, add)
