import pyinotify
import asyncio


path_to_watch = "/home/denis/test"


class MyEventHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        print("CREATE event:", event.pathname)

    def process_IN_DELETE(self, event):
        print("DELETE event:", event.pathname)

    def process_IN_MODIFY(self, event):
        print("MODIFY event:", event.pathname)


def main():
    # watch manager
    wm = pyinotify.WatchManager()
    wm.add_watch(path_to_watch, pyinotify.ALL_EVENTS, rec=True)

    # event handler
    eh = MyEventHandler()

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()

main()