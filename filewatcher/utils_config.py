from json import loads, dumps

DEFAULT_PORT = 25565
SERVER_CONFIG = "/etc/server_config.json"
SERVICE_FILE_NAME = 'fwr-server.service'
SERVICE_FILE = "/lib/systemd/system/{}".format(SERVICE_FILE_NAME)


def read_config() -> [dict, None]:
    try:
        with open(SERVER_CONFIG, 'r') as file_:
            config = loads(file_.read())
        return config
    except FileNotFoundError:
        return {}
    except PermissionError as err:
        print(err)
        return None


def update_config(config_: dict, rewrite=False):
    if not rewrite:
        config = read_config()
        config.update(config_)
        config_ = config

    try:
        with open(SERVER_CONFIG, 'w') as file_:
            file_.write(dumps(config_))
    except PermissionError as err:
        print(err)
