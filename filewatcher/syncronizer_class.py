import pyinotify

from filewatcher.client_class import ClientCommand


class FilesWatcher(pyinotify.ProcessEvent):
    def __init__(self, path: str, host: str, port: int, password: str):
        self.path = path
        self.client = ClientCommand(host, port, password)

        super().__init__()

    def push_all(self):
        pass

    def process_IN_CREATE(self, event):
        print("CREATE event:", event.pathname)

    def process_IN_DELETE(self, event):
        print("DELETE event:", event.pathname)

    def process_IN_MODIFY(self, event):
        print("MODIFY event:", event.pathname)
