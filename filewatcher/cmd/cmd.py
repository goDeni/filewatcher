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
                               action="store_true")
    parser_server.add_argument("--clear",
                               choices=['server', 'remote'],
                               nargs='?')
    parser_server.add_argument("--start",
                               action="store_true")
    parser_server.add_argument("--stop",
                               action="store_true")
    parser_server.add_argument("--auto-start",
                               choices=['enable', 'disable'],
                               nargs='?')

    parser_remote = subparsers.add_parser('remote',
                                          description="Work with remote server",
                                          help="Work with remote server")
    parser_remote.add_argument('--init',
                               action='store_true')
    parser_remote.add_argument('--connect',
                               action='store_true')
    parser_remote.add_argument('--show-folder',
                               nargs='*')
    parser_remote.add_argument('--download',
                               nargs='+')
    parser_remote.add_argument('--upload',
                               nargs='+')
    parser_remote.add_argument('--login',
                               action='store_true')
    args = sys.argv[1:]
    if args and args[0] != 'server':
        args = ['remote'] + args
    return parser.parse_args(args)


def execute_command(command: str, args):
    print(args)
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
