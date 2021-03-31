import contextlib
import functools
import importlib
import logging
import logging.config
import os
import typing

from ..graph import Graph


log = logging.getLogger(__name__)


__all__ = [
    "abs_path",
    "configure_logging",
    "import_object",
    "load_graph",
    "modified_settings",
]


def abs_path(path):
    """Convert ``path`` to normalized, absolute path.

    ``path`` may be a absolute or relative file system path or an asset
    path. Trailing slashes will be retained.

    """
    has_slash = path.endswith(os.sep)
    if not os.path.isabs(path):
        if ":" in path:
            package_name, *rel_path = path.split(":", 1)
            package = importlib.import_module(package_name)
            package_path = os.path.dirname(package.__file__)
            path = os.path.join(package_path, *rel_path)
        else:
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
    path = os.path.normpath(path)
    if has_slash:
        path = f"{path}{os.sep}"
    return path


def configure_logging(settings):
    if settings.testing:
        return

    if settings.log_config_file:
        logging.config.fileConfig(settings.log_config_file)
    else:
        logging.basicConfig(
            format="%(levelname)s [%(name)s] %(message)s", level=settings.log_level
        )
        root_log = logging.getLogger("dijkstar.server")
        root_log.setLevel(settings.log_level)


@functools.lru_cache()
def import_object(path: str, default=None) -> typing.Any:
    """Import object from path.

    Paths have the format ``module_path:object_path``.

    The ``default`` value is returned when ``path`` is ``None``. This is
    a convenience for passing in settings that may be ``None``.

    Examples::

        >>> import_object('dijkstar.graph:Graph')
        <class 'dijkstar.graph.Graph'>
        >>> import_object('dijkstar.graph:Graph.load')
        <bound method Graph.load of <class 'dijkstar.graph.Graph'>>

    """
    if path is None:
        return default
    module_path, object_path = path.split(":")
    module = importlib.import_module(module_path)
    names = object_path.split(".")
    obj = module
    for name in names:
        obj = getattr(obj, name)
    return obj


def load_graph(settings) -> Graph:
    """Load graph based on settings."""
    graph_file = settings.graph_file
    if settings.graph_file:
        graph_file_type = settings.graph_file_type
        if graph_file_type:
            if graph_file_type == "marshal":
                loader = Graph.unmarshal
            elif graph_file_type == "pickle":
                loader = Graph.load
            else:
                raise ValueError("Graph file type must be one of: marshal, pickle")
        else:
            _, ext = os.path.splitext(graph_file)
            if not ext:
                raise ValueError(
                    "Graph file type must be specified via GRAPH_FILE_TYPE or the graph file must "
                    "have a .marshal or .pickle extension"
                )
            elif ext == ".marshal":
                loader = Graph.unmarshal
            elif ext == ".pickle":
                loader = Graph.load
            else:
                raise ValueError(
                    "Graph file extension must be one of: .marshal, .pickle"
                )
        graph = loader(graph_file)
        log.info(f"Loaded graph from {graph_file}")
    else:
        graph = Graph()
        log.info("Created a new graph since no graph file was specified")
    return graph


@contextlib.contextmanager
def modified_settings(**kwargs):
    """Context manager for temporarily modifying settings.

    Mainly useful in tests.

    Usage::

        # Temporarily modify settings.graph_file
        with modified_settings(graph_file='path/to/graph.marshal'):
            graph = load_graph(settings)

    After the ``with`` block, ``settings.graph_file`` will be restored
    automatically to its original value.

    """
    from .conf import settings

    originals = {}
    for name, value in kwargs.items():
        originals[name] = getattr(settings, name)
        setattr(settings, name, value)
    try:
        yield
    finally:
        for name, value in originals.items():
            setattr(settings, name, value)
