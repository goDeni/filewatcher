import os

import pyinotify
from logging import getLogger

from filewatcher.client_class import ClientCommand
from filewatcher.utils import run_forever

log = getLogger(__name__)


class FilesWatcher(pyinotify.ProcessEvent):
    def __init__(self, path: str, host: str, port: int, password: str):
        self.path = path
        self.cut_n = len(path) + 1
        self.client = ClientCommand(host, port, password)
        self.check_tree()

        super().__init__()

    def push_all(self):
        log.warning("Push all")
        for d in os.listdir(self.path):
            self.client.upload(path_source=os.path.join(self.path, d), path_dist='.')

    @run_forever(repeat_delay=300)
    def check_tree(self):
        log.warning("Checking three")
        res = self.client.check_tree(path=self.path)
        res, err = res.get('response'), res.get('err')
        if err:
            log.warning("Error checking three: %s", err)
            return
        if not res:
            return

        for directory in res:
            r = self.client.upload(path_source=os.path.join(self.path, directory), path_dist=os.path.split(directory)[0])
            r, e = r.get('response'), r.get('err')
            if e:
                log.warning("Error uploading file while checking three: %s", e)
            if r:
                log.warning("File %s was uploaded", directory)


    def process_IN_CLOSE_WRITE(self, event):
        path = event.pathname[self.cut_n:]
        log.warning("Modify %s", path)
        path_dist, _ = os.path.split(path)
        if not os.path.exists(event.pathname):
            log.warning("File %s not found", event.pathname)
            return
        try:
            self.client.upload(path_source=event.pathname, path_dist=path_dist)
        except Exception:
            log.exception("process_IN_CLOSE_WRITE error")

    def process_IN_CREATE(self, event):
        path = event.pathname[self.cut_n:]
        log.warning("Create %s", path)
        path_dist, _ = os.path.split(path)
        if not os.path.exists(event.pathname):
            log.warning("File %s not found", event.pathname)
            return
        try:
            self.client.upload(path_source=event.pathname, path_dist=path_dist)
        except Exception:
            log.exception("process_IN_CREATE error")

    def process_IN_DELETE(self, event):
        path = event.pathname[self.cut_n:]
        log.warning("Delete %s", path)
        try:
            self.client.delete(path)
        except Exception:
            log.exception("process_IN_DELETE error")
