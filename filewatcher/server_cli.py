from jinja2 import Environment, PackageLoader
from subprocess import check_call
from os.path import isfile
from getpass import getpass
from filewatcher.utils import (
    update_config,
    read_config,
    SERVICE_FILE_FWR_SERVER,
    DEFAULT_PORT,
    SERVICE_FILE_FWR_SERVER_NAME,
    enter_positive_number,
    encrypt_password,
    enter_path,
)


def create_service_file() -> bool:
    environment = Environment(loader=PackageLoader('filewatcher', 'templates'))
    service_file = environment.get_template(SERVICE_FILE_FWR_SERVER_NAME).render()
    try:
        with open(SERVICE_FILE_FWR_SERVER, 'w') as file_:
            file_.write(service_file)
    except PermissionError as err:
        print(err)
        return False
    return True


def init_server():
    port = enter_positive_number("Enter port[{}]: ".format(DEFAULT_PORT), False, True)
    if not port:
        port = DEFAULT_PORT
    password = encrypt_password(getpass("Enter password: "))
    path = enter_path("Enter absolute path: ")
    if not path:
        return
    update_config({
            'host': '0.0.0.0',
            'port': port,
            'password': password,
            'path': path,
            'synchronize': False,
    }, server_=True, rewrite=True)
    if create_service_file():
        auto_start('enable')
        server('restart')


def clear(delete_ob):
    config = read_config()
    config.pop(delete_ob)
    update_config(config, True)


def server(command: str):
    if isfile(SERVICE_FILE_FWR_SERVER):
        try:
            check_call(['systemctl', command, SERVICE_FILE_FWR_SERVER_NAME])
        except PermissionError as err:
            print(err)
        return
    if command == 'stop':
        return
    if not read_config(server=True):
        print("Enter 'fwr server init' for creating config'")
        return
    if create_service_file():
        server(command)


def auto_start(argument: str):
    if isfile(SERVICE_FILE_FWR_SERVER):
        check_call(['systemctl', argument, SERVICE_FILE_FWR_SERVER_NAME])


def show_config():
    config = read_config(server=True)

    if config:
        print("Server address: {}:{}".format(config['host'], config['port']))
        print("Server path:", config['path'])
    else:
        print("Server config doesn't exist")


def server_command(args):
    if args.init:
        init_server()
    elif args.start or args.stop:
        server('restart' if args.start else 'stop')
    elif args.clear:
        clear(args.clear)
    elif args.auto_start:
        auto_start(args.auto_start)
    else:
        show_config()
