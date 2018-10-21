import os

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
)


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
    }, remote_=True)


def show_config():
    remote_config = read_config().get('remote')

    if remote_config:
        print("Remote server address: {}:{}".format(remote_config['host'], remote_config['port']))
    else:
        print("Remote server config doesnt exist")


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


def login(server: ClientCommand):
    hash_ = server.login()
    if not hash_:
        hash_ = ''
        print("Invalid password")

    if update_config({'password': hash_}, remote_=True) and hash_:
        print("You are successfully authorized!")


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


def remote_command(args):
    if args.init:
        init_remote()
    if True in [args.connect, args.show_folder is not None, args.download is not None, args.upload, args.login]:
        config = read_config().get('remote')
        if not config:
            print("Remote server config doesn't exist")
            return
        server = ClientCommand(config['host'], config['port'], config['password'])
        if args.show_folder is not None:
            show_folder(server, args.show_folder)
        elif args.download is not None:
            download(server, args.download)
        elif args.login:
            login(server)
    else:
        show_config()
