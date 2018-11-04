import os

import pyinotify
from logging import getLogger

from filewatcher.client_class import ClientCommand

log = getLogger(__name__)


class FilesWatcher(pyinotify.ProcessEvent):
    def __init__(self, path: str, host: str, port: int, password: str):
        self.path = path
        self.cut_n = len(path) + 1
        self.client = ClientCommand(host, port, password)
        self.push_all()

        super().__init__()

    def push_all(self):
        log.warning("Push all")
        for d in os.listdir(self.path):
            self.client.upload(path_source=os.path.join(self.path, d), path_dist='.')

    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname[self.cut_n:]
        log.warning("Modify %s", path)
        path_dist, _ = os.path.split(path)
        res = self.client.upload(path_source=event.pathname, path_dist=path_dist)

    def process_IN_CREATE(self, event):
        path = event.pathname[self.cut_n:]
        log.warning("Create %s", path)
        path_dist, _ = os.path.split(path)
        res = self.client.upload(path_source=event.pathname, path_dist=path_dist)

    def process_IN_DELETE(self, event):
        path = event.pathname[self.cut_n:]
        log.warning("Delete %s", path)
        res = self.client.delete(path)

