import os
import pathlib
import shutil
import sys
import textwrap

from runcommands import arg, command
from runcommands.util import abort

from . import __version__


@command(name="dijkstar")
def main(
    subcommand: arg(default=None, help="Command to run"),
    help_: arg(help="Show version, usage, and available subcommands then exit") = False,
    version: arg(help="Show version then exit") = False,
):
    """Dijkstar base command."""
    show_help = help_ or (subcommand is None and not version)
    term_width = min(72, shutil.get_terminal_size((72, 20)).columns)
    if show_help or version:
        print(f"Dijkstar {__version__}")
    if show_help:
        usage = main.arg_parser.format_usage()
        print(f"\n{textwrap.fill(usage, term_width)}\n")
        print("available subcommands:\n")
        fill = max(len(sub.base_name) for sub in main.subcommands) + 4
        short_desc_width = term_width - fill
        for sub in main.subcommands:
            name = f'{f"  {sub.base_name}":<{fill}}'
            lines = textwrap.wrap(sub.short_description, short_desc_width)
            print(name, lines[0], sep="")
            for line in lines[1:]:
                print(" " * fill, line, sep="")
        message = f"Run `{main.name} SUBCOMMAND -h` for subcommand usage/help"
        print("\n", textwrap.fill(message, term_width), sep="")


@main.subcommand
def serve(
    # App config
    #
    # NOTE: All app config args should have a default value of None. If
    # an app config setting isn't specified here, it will be set to the
    # value of its corresponding environment variables, if that's set,
    # or to its default value, specified in the dijkstar.server.conf
    # module. Precedence: command line args > environment > .env.
    env_file: arg(
        short_option="-f",
        help="Env file to load settings from [$PWD/.env, if present]",
    ) = None,
    log_config_file: arg(
        short_option="-l",
        mutual_exclusion_group="logging",
        help="Path to Python logging config file",
    ) = None,
    log_level: arg(
        short_option="-L",
        type=lambda level: level.upper(),
        mutual_exclusion_group="logging",
        help="Log level for basic logging config",
    ) = None,
    template_directory: arg(
        short_option="-t", help="Path to template directory"
    ) = None,
    graph_file: arg(
        short_option="-g",
        help="Path to graph file to load on startup [None; a new graph will be created]",
    ) = None,
    graph_file_type: arg(
        short_option="-T",
        choices=("marshal", "pickle"),
        help="Graph file type [marshal]",
    ) = None,
    read_only: arg(
        short_option="-R",
        type=bool,
        help="Make graph read only by disabling endpoints that modify the graph; this only "
        "applies when a graph file is specified [Don't make read only]",
    ) = None,
    node_serializer: arg(short_option="-n") = None,
    node_deserializer: arg(short_option="-N") = None,
    edge_serializer: arg(short_option="-e") = None,
    edge_deserializer: arg(short_option="-E") = None,
    cost_func: arg(short_option="-c", help="Cost function import path") = None,
    heuristic_func: arg(
        short_option="-u", help="Heuristic function import path"
    ) = None,
    # Uvicorn args
    app: arg(
        short_option="-a",
        help="App import path [dijkstar.server.app:app]",
    ) = "dijkstar.server.app:app",
    root_path: arg(
        short_option="-o",
        help="Set this when server is mounted under a path",
    ) = "",
    host: arg(
        short_option="-H",
        help="Uvicorn host [127.0.0.1]",
    ) = "127.0.0.1",
    port: arg(
        short_option="-p",
        help="Uvicorn port [8000]",
    ) = 8000,
    reload: arg(
        short_option="-r",
        help="Automatically reload uvicorn server when source changes [Don't reload]",
    ) = False,
    workers: arg(
        short_option="-w", type=int, help="Number of uvicorn processes"
    ) = None,
    # Shared app config & uvicorn args
    debug: arg(
        short_option="-d",
        type=bool,
        help="Enable debug mode in both app and uvicorn; will *also* enable auto-reloading "
        "(implies --reload) [Don't debug]",
    ) = None,
    # Info args (show and exit)
    show_settings: arg(
        short_option="-s",
        mutual_exclusion_group="info",
        help="Show app settings [Don't show settings]",
    ) = False,
    show_schema: arg(
        short_option="-S",
        mutual_exclusion_group="info",
        help="Show OpenAPI schema and exit [Don't show schema]",
    ) = False,
):
    """Create Dijkstar server app and run it with uvicorn.

    For app config args (defined in the dijkstar.server.conf module),
    command line args take precedence over environment variables, which
    take precedence over variables specified in the env file.

    """
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        abort(
            1, "Uvicorn not installed; was Dijkstar installed with the `server` extra?"
        )

    import yaml

    if env_file is None:
        default_env_file = pathlib.Path.cwd() / ".env"
        if default_env_file.is_file():
            env_file = default_env_file
    else:
        env_file = pathlib.Path(env_file)
        if not env_file.exists():
            raise FileNotFoundError(f"Env file does not exist: {env_file}")

    reload = reload or debug

    # XXX: This needs to be after args are fully initialized because of
    #      the use of locals().
    def add_to_environ(name, _locals=locals()):
        value = _locals[name]
        if value is not None:
            os.environ[name.upper()] = str(value)

    add_to_environ("env_file")
    add_to_environ("debug")
    add_to_environ("host")
    add_to_environ("port")
    add_to_environ("log_config_file")
    add_to_environ("template_directory")
    add_to_environ("log_level")
    add_to_environ("graph_file")
    add_to_environ("graph_file_type")
    add_to_environ("read_only")
    add_to_environ("node_serializer")
    add_to_environ("node_deserializer")
    add_to_environ("edge_serializer")
    add_to_environ("edge_deserializer")
    add_to_environ("cost_func")
    add_to_environ("heuristic_func")

    # XXX: Dijkstar server imports need to come after environ is set up
    #      so settings will be initialized correctly.
    from .server import utils
    from .server.app import app as starlette_app
    from .server.conf import settings
    from .server.endpoints import schemas

    if show_schema:
        content = schemas.get_schema(starlette_app.routes)
        print("OpenAPI Schema:\n")
        print(yaml.dump(content, default_flow_style=False).strip())
    elif show_settings:
        print(settings)
    else:
        # XXX: Needs be called before uvicorn starts to override its
        #      logging config.
        utils.configure_logging(settings)

        locals_ = locals()
        uvicorn_args = ("root_path", "host", "port", "debug", "reload", "workers")
        uvicorn_args = {n: locals_.get(n) for n in uvicorn_args}
        uvicorn_args = {n: v for (n, v) in uvicorn_args.items() if v is not None}

        if settings.testing:
            # Don't run the server when testing as that will cause the
            # tests to hang.
            return

        uvicorn.run(app, **uvicorn_args)


if __name__ == "__main__":
    sys.exit(main.console_script())
