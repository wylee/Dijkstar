import argparse
import sys

from . import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(prog='dijkstar', add_help=False)
    parser.add_argument(
        '-h', '--help', action='store_true', default=False, help='Show version and help message')
    parser.add_argument(
        '-i', '--info', action='store_true', default=False, help='Show version and usage summary')
    subparsers = parser.add_subparsers()
    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        has_func = hasattr(args, 'func')
        show_help = args.help
        show_info = not show_help and (args.info or not has_func)
        if show_help or show_info:
            print(f'Dijkstar {__version__}')
        if show_help:
            print()
            parser.print_help()
        elif show_info:
            parser.print_usage()
        else:
            args.func(args)


if __name__ == '__main__':
    sys.exit(main())
