import collections
import marshal
import os
from copy import copy

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle


class Graph(collections.MutableMapping):

    """A very simple graph type.

    Its structure looks like this::

        {u: {v: e, ...}, ...}  # Node v is a adjacent to u via edge e

    Edges can be of any type. Nodes have to be hashable since they're
    used as dictionary keys. ``None`` should *not* be used as a node.

    Graphs are *directed* by default. To create an undirected graph, use
    the ``undirected`` flag:

        >>> graph = Graph(undirected=True)

    Note that all this does is automatically add the edge ``(v, u)``
    when ``(u, v)`` is added. In addition, when a node is deleted, its
    incoming nodes will be deleted also.

    """

    def __init__(self, data=None, undirected=False):
        self._data = {}
        self._undirected = undirected
        self._incoming = collections.defaultdict(dict)
        if data is not None:
            self.update(data)

    def __getitem__(self, u):
        return self.get_node(u)

    def __setitem__(self, u, neighbors):
        self.add_node(u, neighbors)

    def __delitem__(self, u):
        self.remove_node(u)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return self.node_count

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._data == other
        return self._data == other._data

    def __repr__(self):
        return repr(self._data)

    def get_data(self):
        """Return the underlying data dict."""
        return self._data

    def subgraph(self, nodes, disconnect=False):
        """Get a subgraph with the specified nodes.

        If ``disconnect`` is specified, the nodes will be disconnected
        from each other; this is useful when creating annex graphs.

        """
        subgraph = self.__class__()
        for u in nodes:
            neighbors = self[u]
            for v, edge in neighbors.items():
                u, v, edge = copy(u), copy(v), copy(edge)
                subgraph.add_edge(u, v, edge)
        if disconnect:
            for u in nodes:
                neighbors = subgraph[u]
                for v in nodes:
                    if v in neighbors:
                        del neighbors[v]
        return subgraph

    def add_edge(self, u, v, edge=None):
        """Add an ``edge`` from ``u`` to ``v``.

        If the graph is undirected, the ``edge`` will be added from
        ``v`` to ``u`` also.

        """
        data = self._data
        incoming = self._incoming
        undirected = self._undirected

        if u in data:
            neighbors = data[u]
            neighbors[v] = edge
        else:
            data[u] = {v: edge}
        incoming[v][u] = edge

        if undirected:
            if v in data:
                neighbors = data[v]
                neighbors[u] = edge
            else:
                data[v] = {u: edge}
            incoming[u][v] = edge

        return edge

    def get_edge(self, u, v):
        """Get edge ``(u, v)``."""
        return self._data[u][v]

    def remove_edge(self, u, v):
        """Remove edge ``(u, v)``."""
        data = self._data
        incoming = self._incoming
        del data[u][v]
        del incoming[v][u]
        if not incoming[v]:
            del incoming[v]
        if u in data[v]:
            del data[v][u]
            del incoming[u][v]
            if not incoming[u]:
                del incoming[u]

    @property
    def edge_count(self):
        count = sum(len(neighbors) for neighbors in self._data.values())
        if self._undirected:
            assert count % 2 == 0
            count = count // 2
        return count

    def add_node(self, u, neighbors=None):
        """Add node ``u`` and, optionally, its ``neighbors``.

        Adds or updates the node ``u``. If ``u`` isn't already in the
        graph, it will be created with the specified ``neighbors``. If
        it is, it will be updated with the specified ``neighbors``.

        Note that if ``u`` is already in the graph, only its existing
        neighbors that are *also* specified in ``neighbors`` will be
        affected; other neighbors will be left as is. To clear a node
        completely, use ``del graph[u]``.

        ``neighbors``
            An optional dict of neighbors like ``{v1: e1, v2: e2, ...}``.

        """
        data = self._data
        incoming = self._incoming
        undirected = self._undirected
        directed = not undirected

        if neighbors is None:
            neighbors = {}

        if directed or u not in data:
            # For a directed graph, add u if it's not present or replace
            # it completely if is.
            #
            # For an undirected graph, add u if it's not present. If it
            # is, add new neighbors and update existing neighbors, but
            # leave other neighbors alone.
            data[u] = {}

        node_data = data[u]

        for v, e in neighbors.items():
            node_data[v] = e
            incoming[v][u] = e
            if undirected:
                if v not in data:
                    data[v] = {u: e}
                else:
                    data[v][u] = e
                incoming[u][v] = e

        return node_data

    def get_node(self, u):
        """Get node ``u``."""
        return self._data[u]

    def remove_node(self, u):
        """Remove node ``u``.

        In addition to removing the node itself from the underlying data
        dict, which in turn removes its outgoing edges, this also
        removes the node's incoming edges.

        """
        data = self._data
        incoming = self._incoming
        neighbors = data[u]

        for v in incoming[u]:
            del data[v][u]
        for v in neighbors:
            del incoming[v][u]
            if not incoming[v]:
                del incoming[v]

        del data[u]
        del incoming[u]

    @property
    def node_count(self):
        return len(self._data)

    def get_incoming(self, v):
        return self._incoming[v]

    @classmethod
    def _read(cls, reader, from_):
        """Read from path or open file using specified reader."""
        if isinstance(from_, str):
            with open(from_, 'rb') as fp:
                data = reader(fp)
        else:
            data = reader(from_)
        return cls(data)

    def _write(self, writer, to):
        """Write to path or open file using specified writer."""
        if isinstance(to, str):
            with open(to, 'wb') as fp:
                writer(self._data, fp)
        else:
            writer(self._data, to)

    @classmethod
    def guess_load(cls, from_, ext=None):
        """Read graph based on extension or attempt all loaders.

        If a file name with an extension is passed *or* a file and an
        extension are passed, load the graph from the file based on the
        extension.

        Otherwise, try to load the file using pickle, and if that fails,
        with marshal.

        """
        if not ext and isinstance(from_, str):
            _, ext = os.path.splitext(from_)
        if ext:
            ext = ext.lstrip('.')
        if ext == 'pickle':
            return cls.load(from_)
        elif ext == 'marshal':
            return cls.unmarshal(from_)
        try:
            return Graph.load(from_)
        except pickle.UnpicklingError:
            from_.seek(0)
            try:
                # NOTE: We don't simply call Graph.unmarshal() here
                # because errors raised by Graph._read() when it calls
                # Graph(data) could be conflated with errors raised by
                # marshal.load().
                data = marshal.load(from_)
            except (EOFError, ValueError, TypeError):
                pass
            else:
                return cls(data)
        raise ValueError(
            'Could not guess how to load graph; Graph.guess_load() requires either a file with '
            'a .pickle or .marshal extension, for the extension/type of the file to be specified, '
            'or for the file to be loadable with Graph.load() or Graph.unmarshal().')

    @classmethod
    def load(cls, from_):
        """Read graph using pickle."""
        return cls._read(pickle.load, from_)

    def dump(self, to):
        """Write graph using pickle."""
        self._write(pickle.dump, to)

    @classmethod
    def unmarshal(cls, from_):
        """Read graph using marshal.

        Marshalling is quite a bit faster than pickling, but only the
        following types are supported: booleans, integers, long
        integers, floating point numbers, complex numbers, strings,
        Unicode objects, tuples, lists, sets, frozensets, dictionaries,
        and code objects.

        """
        return cls._read(marshal.load, from_)

    def marshal(self, to):
        """Write graph using marshal."""
        self._write(marshal.dump, to)
