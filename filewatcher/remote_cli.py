import os
from os.path import isfile
from subprocess import check_call

from jinja2 import Environment, PackageLoader

from filewatcher.client_class import ClientCommand
from filewatcher.utils import (
    enter_positive_number,
    human_file_size,
    update_config,
    read_config,
    DEFAULT_PORT,
    enter_ip,
    TableRender,
    format_time,
    enter_path,
    SERVICE_FILE_FWR_SYNC_NAME,
    SERVICE_FILE_FWR_SYNC
)


def create_service_file_synchronizer() -> bool:
    if isfile(SERVICE_FILE_FWR_SYNC):
        return True

    environment = Environment(loader=PackageLoader('filewatcher', 'templates'))
    service_file = environment.get_template(SERVICE_FILE_FWR_SYNC_NAME).render()
    try:
        with open(SERVICE_FILE_FWR_SYNC, 'w') as file_:
            file_.write(service_file)
    except PermissionError as err:
        print(err)
        return False
    return True


def client_command(put_config=False, server_connect=True, synchronize_block=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            server = None
            config = read_config(remote=True)
            if synchronize_block and server_connect and config.get('synchronize'):
                print("Synchronize enabled. You can't do this operation")
                return
            if not config:
                print("Remote server config doesn't exist")
                return
            if server_connect:
                server = ClientCommand(config['host'], config['port'], config['password'])
                args = (server,) + args

            if put_config:
                kwargs['config'] = config

            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                if server is not None:
                    server.close()
        return wrapper
    return decorator


def init_remote():
    host = enter_ip("Enter server ip: ")
    if not host:
        return
    port = enter_positive_number("Enter port server[{}]: ".format(DEFAULT_PORT), False, True)
    if not port:
        port = DEFAULT_PORT
    update_config({
            'port': port,
            'host': host,
            'password': '',
            'synchronize': False,
            'synchronize-path': '',
    }, remote_=True, rewrite=True)


def synchronize(status: str):
    if not create_service_file_synchronizer():
        return

    path_to_watch = ''
    status = status == 'enable'

    if status:
        path_to_watch = enter_path('Enter absolute path to watching: ')

    update_config({'synchronize': status, 'synchronize-path': path_to_watch}, remote_=True)

    check_call(['systemctl', 'enable' if status else 'disable', SERVICE_FILE_FWR_SYNC_NAME])
    check_call(['systemctl', 'restart' if status else 'stop', SERVICE_FILE_FWR_SYNC_NAME])

    print("Synchronize successfully", 'enabled' if status else 'disabled')


@client_command(put_config=True, server_connect=False)
def show_config(config: dict):
    if config:
        print("Remote server address: {}:{}".format(config.get('host'), config.get('port')))
        print("Synchronize:", 'Enabled' if config.get('synchronize') else 'Disabled')
        if config.get('synchronize'):
            print("Synchronize path:", config.get('synchronize-path'))
    else:
        print("Remote server config doesnt exist")


@client_command(synchronize_block=False)
def show_folder(server: ClientCommand, folders_to_show: list):
    if not folders_to_show:
        folders_to_show.append('.')

    for folder in folders_to_show:
        directory, err = server.show_folder(folder)
        if err:
            print(err)
            continue

        files, folders = directory['files'], directory['folders']
        table = TableRender()
        num = 0

        for num, file in enumerate(sorted(folders, key=lambda a: a[0]), 1):
            name, size, time_change = file
            table.write_in_column("№", num)
            table.write_in_column("NAME", name)
            table.write_in_column("TYPE", "FOLDER")
            table.write_in_column("SIZE", human_file_size(size))
            table.write_in_column("TIME-CHANGE", format_time(time_change))

        for name, size, time_change in sorted(files, key=lambda a: a[0]):
            num += 1
            table.write_in_column("№", num)
            table.write_in_column("NAME", name)
            table.write_in_column("TYPE", "FILE")
            table.write_in_column("SIZE", human_file_size(size))
            table.write_in_column("TIME-CHANGE", format_time(time_change))

        print("Folder", folder)
        print(table.render() if num else "Empty", '\n')


@client_command(synchronize_block=False)
def login(server: ClientCommand):
    hash_ = server.login()
    if not hash_:
        hash_ = ''
        print("Invalid password")

    if update_config({'password': hash_}, remote_=True) and hash_:
        print("You are successfully authorized!")


@client_command(synchronize_block=False)
def download(server: ClientCommand, args: list):
    path_from = args[:-1] if len(args) > 1 else [args[-1]]
    path_to = args[-1] if len(args) > 1 else os.path.abspath('')

    if not os.path.isdir(path_to):
        print("Invalid destination path")
        return

    for path in path_from:
        res = server.download(path, path_to)
        res, err = res.get('response'), res.get('err')
        if err:
            print("Error:", err)
        if res:
            print("Successful download", path, '\n')


@client_command()
def upload(server: ClientCommand, args: list):
    what_path = args[:-1] if len(args) > 1 else [args[-1]]
    path_to = args[-1] if len(args) > 1 else '.'

    for path in what_path:
        if not (os.path.isdir(path) or os.path.isfile(path)):
            print("Invalid path", path)
            continue
        res = server.upload(path, path_to)
        res, err = res.get('response'), res.get('err')
        if err:
            print("Error:", err)
        if res:
            print("{} uploaded".format(path))


@client_command()
def remove(server: ClientCommand, delete_objects: list):
    for delete_obj in delete_objects:
        res = server.delete(delete_obj)
        res, err = res.get('response'), res.get('err')
        if err:
            print("Error:", err)
            continue
        if res:
            print(delete_obj, "Deleted")


@client_command(put_config=True, server_connect=False)
def synchronize_all(config: dict):
    if not config:
        return
    if not config['synchronize']:
        print("Synchronize not configured")
        return
    print("Synchronizing...")
    check_call(['systemctl', 'restart', SERVICE_FILE_FWR_SYNC_NAME])


@client_command()
def rename(server: ClientCommand, rename_d: list):
    res = server.rename(rename_d)
    res, err = res.get('response'), res.get('err')
    if err:
        print(err)
    if res:
        print("Renamed successfully", ' -> '.join(rename_d))


@client_command()
def move(server: ClientCommand, move_d: list):
    res = server.move(move_d)
    res, err = res.get('response'), res.get('err')
    if err:
        print(err)
    if res:
        print("Moved successfully", ' -> '.join(move_d))


@client_command()
def copy(server: ClientCommand, copy_d: list):
    res = server.copy(copy_d)
    res, err = res.get('response'), res.get('err')
    if err:
        print(err)
    if res:
        print("Сopied successfully", ' -> '.join(copy_d))


def remote_command(args):
    if args.init:
        init_remote()
    elif args.show_folder is not None:
        show_folder(args.show_folder)
    elif args.download:
        download(args.download)
    elif args.upload:
        upload(args.upload)
    elif args.login:
        login()
    elif args.synchronize:
        synchronize(args.synchronize)
    elif args.synchronize_all:
        synchronize_all()
    elif args.remove:
        remove(args.remove)
    elif args.rename:
        rename(args.rename)
    elif args.move:
        move(args.move)
    elif args.copy:
        copy(args.copy)
    else:
        show_config()
