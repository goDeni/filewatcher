from logging import getLogger

import pyinotify

from filewatcher import backend
from filewatcher.utils import read_config
from filewatcher.syncronizer_class import FilesWatcher

log = getLogger(__name__)

CONFIGURATION = read_config(remote=True)


def main():
    args = backend.default_arg_parser(__name__)
    backend.setup_logging(args.debug)

    status, path_to_watch = CONFIGURATION.get('synchronize'), CONFIGURATION.get('synchronize-path')

    if not status:
        backend.systemd_notify(backend.READY)
        log.warning("Synchronize status: %s", status)
        return

    wm = pyinotify.WatchManager()
    wm.add_watch(path_to_watch, pyinotify.ALL_EVENTS, rec=True, auto_add=True)

    host = CONFIGURATION['host']
    port = int(CONFIGURATION['port'])
    password = CONFIGURATION['password']

    eh = FilesWatcher(path=path_to_watch, host=host, port=port, password=password)

    notifier = pyinotify.Notifier(wm, eh)

    backend.systemd_notify(backend.READY)
    try:
        notifier.loop()
    except KeyboardInterrupt:
        pass
    except Exception as err:
        log.exception("Synchronizer failed")

    notifier.stop()


if __name__ == "__main__":
    main()
