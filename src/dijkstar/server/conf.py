import os
import pathlib
import re
import sys
import textwrap

from starlette.config import Config

from . import utils


__all__ = ["settings"]


class Settings:

    """Container for settings."""

    def __init__(self, **data):
        config = Config(os.getenv("ENV_FILE"))

        docs = {}
        defaults = {}

        for name, kwargs in data.items():
            callable_default = kwargs.pop("callable_default", None)
            if callable_default:
                kwargs["default"] = callable_default(self)

            default = kwargs.setdefault("default", None)
            cast = kwargs.setdefault("cast", None)

            docs[name] = kwargs.pop("doc", None)
            defaults[name] = config._perform_cast(name, default, cast)

            value = config(name.upper(), **kwargs)
            setattr(self, name, value)

        self.__docs = docs
        self.__defaults = defaults

    def __str__(self):
        items = []
        for name in self.__dict__:
            if not name.startswith("_"):
                value = getattr(self, name)

                default = self.__defaults[name]
                is_default = value == default

                doc = self.__docs.get(name) or ""
                if doc:
                    doc = textwrap.fill(doc, 68)
                    doc = textwrap.indent(doc, "    ")
                    doc = f"\n{doc}"
                if not is_default:
                    doc = f"{doc}\n    [{default!r}]"

                items.append(f"{name.upper()} = {value!r}{doc}")
        return "\n".join(items)


def testing_default(_settings):
    return bool(
        "TESTING" not in os.environ
        and sys.argv
        and re.match(r".*python\d? -m unittest", sys.argv[0])
    )


settings = Settings(
    debug={
        "cast": bool,
        "default": False,
    },
    testing={
        "doc": "Indicates tests are being run",
        "cast": bool,
        "callable_default": testing_default,
    },
    host={
        "doc": "Server host",
        "default": "127.0.0.1",
    },
    port={"doc": "Server port", "cast": int, "default": 8000},
    log_config_file={
        "doc": "Path to Python logging config file (see "
        "https://docs.python.org/3/library/logging.config.html)",
        "cast": utils.abs_path,
    },
    log_level={
        "doc": "Log level for basic logging config; ignored if LOG_CONFIG_FILE is specified",
        "callable_default": lambda s: "DEBUG" if s.debug else "INFO",
    },
    template_directory={
        "doc": "Path to directory containing HTML/Jinja2 templates",
        "default": str(pathlib.Path(__file__).parent / "templates"),
        "cast": utils.abs_path,
    },
    graph_file={
        "doc": "Path to graph file (a marshal or pickle file) to read on startup; if not "
        "specified, a new empty graph will be created",
        "cast": utils.abs_path,
    },
    graph_file_type={
        "doc": "One of marshal or pickle; only required if GRAPH_FILE setting doesn't have a "
        ".marshal or .pickle extension",
    },
    read_only={
        "doc": "Make graph read only (disable modifying endpoints)",
        "cast": bool,
        "default": False,
    },
    node_serializer={
        "doc": "Serializer for converting nodes to JSON keys",
        "cast": utils.import_object,
        "default": "json:dumps",
    },
    node_deserializer={
        "doc": "Type for converting URL params and JSON keys to nodes",
        "cast": utils.import_object,
        "default": "json:loads",
    },
    edge_serializer={
        "doc": "Serializer for converting nodes to JSON keys",
        "cast": utils.import_object,
        "default": "json:dumps",
    },
    edge_deserializer={
        "doc": "Type for converting URL params and JSON keys to nodes",
        "cast": utils.import_object,
        "default": "json:loads",
    },
    cost_func={
        "doc": "Default cost function",
        "cast": utils.import_object,
    },
    heuristic_func={
        "doc": "Default heuristic function",
        "cast": utils.import_object,
    },
)
