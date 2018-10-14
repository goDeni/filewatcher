from json import loads
from logging import getLogger

from filewatcher import backend
from filewatcher.utils import SERVER_CONFIG
from filewatcher.server_class import ServerFwr

log = getLogger(__name__)

with open(SERVER_CONFIG, 'r') as file_:
    CONFIGURATION = loads(file_.read()).get('server')


def main():
    args = backend.default_arg_parser(__name__)
    backend.setup_logging(args.debug)

    server = ServerFwr(CONFIGURATION['host'], CONFIGURATION['port'], CONFIGURATION['password'])
    backend.systemd_notify(backend.READY)
    try:
        server.listen()
    except Exception:
        log.exception("Error")


if __name__ == "__main__":
    main()
