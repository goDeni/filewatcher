from json import loads
from logging import getLogger

from filewatcher import backend
from filewatcher.server_class import ServerFwr
from filewatcher.utils_config import SERVER_CONFIG

log = getLogger(__name__)

with open(SERVER_CONFIG, 'r') as file_:
    CONFIGURATION = loads(file_.read()).get('server')


def main():
    args = backend.default_arg_parser(__name__)
    backend.setup_logging(args.debug)

    server = ServerFwr(CONFIGURATION['host'], CONFIGURATION['port'], CONFIGURATION['password'], CONFIGURATION['path'])
    backend.systemd_notify(backend.READY)
    try:
        server.listen()
    except Exception:
        log.exception("Error")
    server.close()


if __name__ == "__main__":
    main()
