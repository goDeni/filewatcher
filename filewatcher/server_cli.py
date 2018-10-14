from json import loads, dumps
from jinja2 import Environment, PackageLoader
from subprocess import check_call
from os.path import isfile
from filewatcher.utils import (
    enter_positive_number,
    enter_string,
    enter_ip,
    SERVER_CONFIG,
)


DEFAULT_PORT = 25565

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


def create_service_file() -> bool:
    environment = Environment(loader=PackageLoader('filewatcher', 'templates'))
    service_file = environment.get_template(SERVICE_FILE_NAME).render()
    try:
        with open(SERVICE_FILE, 'w') as file_:
            file_.write(service_file)
    except PermissionError as err:
        print(err)
        return False
    return True


def init_server():
    port = enter_positive_number("Enter port[{}]: ".format(DEFAULT_PORT), False, True)
    if not port:
        port = DEFAULT_PORT
    password = enter_string("Enter password: ")
    update_config({
        'server': {
            'host': '0.0.0.0',
            'port': port,
            'password': password,
        }
    })
    if create_service_file():
        auto_start('enable')
        server('restart')


def connect_server():
    host = enter_ip("Enter server ip: ")
    if not host:
        return
    port = enter_positive_number("Enter port server[{}]: ".format(DEFAULT_PORT), False, True)
    if not port:
        port = DEFAULT_PORT
    password = input("Enter password: ")
    update_config({
        'remote': {
            'port': port,
            'host': host,
            'password': password,
        }
    })


def clear(delete_ob):
    config = read_config()
    config.pop(delete_ob)
    update_config(config, True)


def server(command: str):
    if isfile(SERVICE_FILE):
        try:
            check_call(['systemctl', command, SERVICE_FILE_NAME])
        except PermissionError as err:
            print(err)
        return
    if command == 'stop':
        return
    if not read_config().get('server'):
        print("Enter 'fwr server init' for creating config'")
        return
    if create_service_file():
        server(command)


def auto_start(argument: str):
    if isfile(SERVICE_FILE):
        check_call(['systemctl', argument, SERVICE_FILE_NAME])


def show_config():
    config = read_config()
    server_config = config.get('server')
    remote_config = config.get('remote')

    if server_config:
        print("Server address: {}:{}".format(server_config['host'], server_config['port']))
    if remote_config:
        print("Remote server address: {}:{}".format(remote_config['host'], remote_config['port']))


def server_command(args):
    if args.init:
        init_server()
    elif args.start or args.stop:
        server('start' if args.start else 'stop')
    elif args.clear:
        clear(args.clear)
    elif args.auto_start:
        auto_start(args.auto_start)
    elif args.connect:
        connect_server()
    else:
        show_config()
