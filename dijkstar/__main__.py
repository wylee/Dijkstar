import argparse
import os
import pathlib
import sys

from . import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(prog='dijkstar', add_help=False)
    parser.add_argument(
        '-h', '--help', action='store_true', default=False, help='Show version and help message')
    parser.add_argument(
        '-i', '--info', action='store_true', default=False, help='Show version and usage summary')
    subparsers = parser.add_subparsers()
    add_serve_command(subparsers)
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


def add_serve_command(subparsers):
    # XXX: Heuristic for determining if server functionality is
    #      installed.
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        return

    parser = subparsers.add_parser(
        'serve', description='Create Dijkstar server app and run it with uvicorn')

    parser.set_defaults(func=serve)

    # App config
    parser.add_argument(
        '-f', '--env-file', help='Env file to load settings from [$PWD/.env, if present]')

    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument('-l', '--log-config-file', help='Path to Python logging config file')
    log_group.add_argument(
        '-L', '--log-level', type=lambda level: level.upper(),
        help='Log level for basic logging config')

    parser.add_argument('-t', '--template-directory', help='Path to template directory')

    parser.add_argument(
        '-g', '--graph-file',
        help='Path to graph file to load on startup [None; a new graph will be created]')
    parser.add_argument(
        '-T', '--graph-file-type', choices=('marshal', 'pickle'), help='Graph file type [marshal]')
    parser.add_argument(
        '-R', '--read-only', action='store_true', default=None,
        help='Make graph read only by disabling endpoints that modify the graph; this only '
             'applies when a graph file is specified [Don\'t make read only]')

    parser.add_argument('-n', '--node-serializer')
    parser.add_argument('-N', '--node-deserializer')
    parser.add_argument('-e', '--edge-serializer')
    parser.add_argument('-E', '--edge-deserializer')

    # Uvicorn args
    parser.add_argument(
        '-a', '--app', default='dijkstar.server.app:app',
        help='App import path [dijkstar.server.app:app]')
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Uvicorn host [127.0.0.1]')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Uvicorn port [8000]')
    parser.add_argument(
        '-r', '--reload', action='store_true', default=None,
        help='Automatically reload uvicorn server when source changes [Don\'t reload]')
    parser.add_argument('-w', '--workers', type=int, help='Number of uvicorn processes')

    # Shared app config & uvicorn args
    parser.add_argument(
        '-d', '--debug', action='store_true', default=None,
        help='Enable debug mode in both app and uvicorn; will *also* enable auto-reloading'
             '(implies --reload) [Don\'t debug]')

    # Info args (show and exit)
    serve_show_group = parser.add_mutually_exclusive_group()

    serve_show_group.add_argument(
        '-s', '--show-settings', action='store_true',
        help='Show app settings [Don\'t show settings]')

    serve_show_group.add_argument(
        '-S', '--show-schema', action='store_true',
        help='Show OpenAPI schema and exit [Don\'t show schema]')


def serve(args):
    import uvicorn
    import yaml

    def add_to_environ(name, value=None):
        if value is None:
            value = getattr(args, name)
        if value is not None:
            os.environ[name.upper()] = str(value)

    env_file = args.env_file
    if env_file is None:
        default_env_file = pathlib.Path.cwd() / pathlib.Path('.env')
        if default_env_file.is_file():
            env_file = default_env_file
    else:
        env_file = pathlib.Path(env_file)
        if not env_file.exists():
            raise FileNotFoundError(f'Env file does not exist: {env_file}')

    add_to_environ('env_file', env_file)
    add_to_environ('debug')
    add_to_environ('host')
    add_to_environ('port')
    add_to_environ('log_config_file')
    add_to_environ('template_directory')
    add_to_environ('log_level')
    add_to_environ('graph_file')
    add_to_environ('graph_file_type')
    add_to_environ('read_only')
    add_to_environ('node_serializer')
    add_to_environ('node_deserializer')
    add_to_environ('edge_serializer')
    add_to_environ('edge_deserializer')

    # XXX: Dijkstar server imports need to come after environ is set up
    #      so settings will be initialized correctly.
    from .server import utils
    from .server.app import app
    from .server.conf import settings
    from .server.endpoints import schemas

    if args.show_schema:
        content = schemas.get_schema(app.routes)
        print('OpenAPI Schema:\n')
        print(yaml.dump(content, default_flow_style=False).strip())
    elif args.show_settings:
        print(settings)
    else:
        # XXX: Needs be called before uvicorn starts to override its
        #      logging config.
        utils.configure_logging(settings)

        uvicorn_args = ('host', 'port', 'debug', 'reload', 'workers')
        uvicorn_args = {n: getattr(args, n) for n in uvicorn_args}
        uvicorn_args = {n: v for (n, v) in uvicorn_args.items() if v is not None}

        if settings.testing:
            # Don't run the server when testing as that will cause the
            # tests to hang.
            return

        uvicorn.run(args.app, **uvicorn_args)


if __name__ == '__main__':
    sys.exit(main())
