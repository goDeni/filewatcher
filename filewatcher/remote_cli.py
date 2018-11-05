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


def client_command(func):
    def wrrapper(*args, **kwargs):
        config = read_config(remote=True)
        if not config:
            print("Remote server config doesn't exist")
            return
        server = ClientCommand(config['host'], config['port'], config['password'])
        try:
            return func(server, *args, **kwargs)
        except KeyboardInterrupt:
            server.close()
    return wrrapper


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


def show_config():
    remote_config = read_config(remote=True)
    if remote_config:
        print("Remote server address: {}:{}".format(remote_config.get('host'), remote_config.get('port')))
        print("Synchronize:", 'Enabled' if remote_config.get('synchronize') else 'Disabled')
        if remote_config.get('synchronize'):
            print("Synchronize path:", remote_config.get('synchronize-path'))
    else:
        print("Remote server config doesnt exist")


@client_command
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


@client_command
def login(server: ClientCommand):
    hash_ = server.login()
    if not hash_:
        hash_ = ''
        print("Invalid password")

    if update_config({'password': hash_}, remote_=True) and hash_:
        print("You are successfully authorized!")


@client_command
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


@client_command
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


@client_command
def delete(server: ClientCommand, delete_objects: list):
    for delete_obj in delete_objects:
        res = server.delete(delete_obj)
        res, err = res.get('response'), res.get('err')
        if err:
            print("Error:", err)
            continue
        if res:
            print(delete_obj, "Deleted")


def synchronize_all():
    config = read_config(remote=True)
    if not config:
        return
    if not config['synchronize']:
        print("Synchronize not configured")
        return
    print("Synchronizing...")
    check_call(['systemctl', 'restart', SERVICE_FILE_FWR_SYNC_NAME])


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
    elif args.delete:
        delete(args.delete)
    else:
        show_config()
