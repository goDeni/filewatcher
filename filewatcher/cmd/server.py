from logging import getLogger

from filewatcher import backend
from filewatcher.server_class import ServerFwr
from filewatcher.utils import read_config

log = getLogger(__name__)

CONFIGURATION = read_config(server=True)


def main():
    args = backend.default_arg_parser(__name__)
    backend.setup_logging(args.debug)
    # sudo chmod -R a+rwx <folder>
    server = ServerFwr(CONFIGURATION['host'], CONFIGURATION['port'], CONFIGURATION['password'], CONFIGURATION['path'])
    backend.systemd_notify(backend.READY)
    try:
        server.listen()
    except KeyboardInterrupt:
        pass
    except Exception:
        log.exception("Error")
    finally:
        server.close()


if __name__ == "__main__":
    main()
