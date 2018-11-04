from json import loads, dumps
from logging import getLogger

log = getLogger(__name__)

DEFAULT_PORT = 25565
SERVER_CONFIG = "/etc/server_config.json"

SERVICE_FILE_FWR_SERVER_NAME = 'fwr-server.service'
SERVICE_FILE_FWR_SYNC_NAME = 'fwr-sync.service'

SERVICE_FILE_FWR_SERVER = "/lib/systemd/system/{}".format(SERVICE_FILE_FWR_SERVER_NAME)
SERVICE_FILE_FWR_SYNC = "/lib/systemd/system/{}".format(SERVICE_FILE_FWR_SYNC_NAME)


def read_config(remote=False, server=False) -> [dict, None]:
    try:
        with open(SERVER_CONFIG, 'r') as file_:
            config = loads(file_.read())
        if remote and not server:
            return config['remote']
        if server and not remote:
            return config['server']
        return config
    except FileNotFoundError:
        return {}
    except PermissionError as err:
        print(err)
        return None


def update_config(config_: dict, rewrite=False, remote_=False, server_=False) -> bool:
    if not rewrite or (rewrite and True in [remote_, server_]):
        config = read_config()
        if remote_:
            if rewrite:
                config['remote'] = config_
            else:
                config['remote'].update(config_)
        elif server_:
            if rewrite:
                config['server'] = config_
            else:
                config['server'].update(config_)
        else:
            config.update(config_)
        config_ = config

    try:
        with open(SERVER_CONFIG, 'w') as file_:
            file_.write(dumps(config_))
        return True
    except PermissionError as err:
        print(err)
        log.exception("Update config error")
    return False
