#!/usr/bin/env python3
import sys
from argparse import ArgumentParser

from filewatcher.server_cli import server_command
from filewatcher.remote_cli import remote_command


def parse_args():
    parser = ArgumentParser(description='filewatcher CLI')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_server = subparsers.add_parser('server',
                                           description="Work with server",
                                           help="Work with server")

    parser_server.add_argument("--init",
                               action="store_true",
                               help="Initialization server")
    parser_server.add_argument("--clear",
                               choices=['server', 'remote'],
                               nargs='?',
                               help="Clear server/remote config")
    parser_server.add_argument("--start",
                               action="store_true",
                               help="Start server")
    parser_server.add_argument("--stop",
                               action="store_true",
                               help="Stop server")
    parser_server.add_argument("--auto-start",
                               choices=['enable', 'disable'],
                               nargs='?',
                               help="Enable or disable auto-start server")
    parser_server.add_argument('-shc', '--show-config',
                               action='store_true',
                               help="Show server configuration")

    parser_remote = subparsers.add_parser('remote',
                                          description="Work with remote server",
                                          help="Work with client")
    parser_remote.add_argument('-i', '--init',
                               action='store_true',
                               help="Initialization server for remote access")
    parser_remote.add_argument('-l', '--login',
                               action='store_true',
                               help="Authorization on server")
    parser_remote.add_argument('-shf', '--show-folder',
                               nargs='*',
                               help="Show files and folders in remote folder")
    parser_remote.add_argument('-del', '--delete',
                               nargs='+',
                               help="Delete files/folders in remote folder")
    parser_remote.add_argument('-rn', '--rename',
                               nargs=2,
                               help="Rename folder/file in remote folder")
    parser_remote.add_argument('-mv', '--move',
                               nargs=2,
                               help="Moving folder/file on remote folder")
    parser_remote.add_argument('-shc', '--show-config',
                               action='store_true',
                               help="Show client configuration")
    parser_remote.add_argument('-d', '--download',
                               nargs='+',
                               help="Download folders/files from server")
    parser_remote.add_argument('-u', '--upload',
                               nargs='+',
                               help="Upload folders/files on server")
    parser_remote.add_argument('-sync', '--synchronize',
                               choices=['enable', 'disable'],
                               nargs='?',
                               help="Enable or disable synchronization local folder with folder on the server")
    parser_remote.add_argument('--synchronize-all',
                               action='store_true',
                               help="Restart synchronize")

    args = sys.argv[1:]
    if args and args[0] != 'server' and args[0] not in ['--help', '-h']:
        args = ['remote'] + args
    return parser.parse_args(args)


def execute_command(command: str, args):
    if command == 'server':
        server_command(args)
    elif command == 'remote':
        remote_command(args)


def main():
    args = parse_args()
    try:
        execute_command(args.command, args)
    except KeyboardInterrupt:
        print("\nExit")


if __name__ == '__main__':
    main()
