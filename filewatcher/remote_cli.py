from filewatcher.server_cli import DEFAULT_PORT
from filewatcher.utils import enter_positive_number, enter_ip
from filewatcher.utils_config import update_config, read_config
from filewatcher.client_class import ClientCommand


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


def show_folder(server: ClientCommand):
    directory, err = server.show_folder()
    print(directory, err)
    if err:
        print("Invalid password")
        return


def login(server: ClientCommand):
    hash_ = server.login()
    if not hash_:
        hash_ = ''
        print("Invalid password")

    if update_config({'password': hash_}, remote_=True) and hash_:
        print("You are successfully authorized!")


def remote_command(args):
    if args.init:
        init_remote()
    if True in [args.connect, args.show_folder, args.download, args.upload, args.login]:
        config = read_config().get('remote')
        if not config:
            print("Remote server config doesn't exist")
            return
        server = ClientCommand(config['host'], config['port'], config['password'])
        if args.show_folder:
            show_folder(server)
        elif args.login:
            login(server)
    else:
        show_config()
