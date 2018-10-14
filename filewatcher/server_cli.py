from jinja2 import Environment, PackageLoader
from subprocess import check_call
from os.path import isfile
from filewatcher.utils_config import (
    update_config,
    read_config,
    SERVICE_FILE,
    DEFAULT_PORT,
    SERVICE_FILE_NAME,
)
from filewatcher.utils import (
    enter_positive_number,
    enter_string,
    enter_path,
)


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
    path = enter_path("Enter absolute path: ")
    if not path:
        return
    update_config({
        'server': {
            'host': '0.0.0.0',
            'port': port,
            'password': password,
            'path': path,
        }
    })
    if create_service_file():
        auto_start('enable')
        server('restart')


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

    if server_config:
        print("Server address: {}:{}".format(server_config['host'], server_config['port']))
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
