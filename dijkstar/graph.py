import collections
import marshal

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

    """

    def __init__(self, data=None):
        self._data = {}
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

    def get_data(self):
        """Return the underlying data dict."""
        return self._data

    def add_edge(self, u, v, edge=None):
        """Add an ``edge`` from ``u`` to ``v``."""
        if u in self:
            neighbors = self[u]
            neighbors[v] = edge
        else:
            self[u] = {v: edge}
        self._incoming[v][u] = edge
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
        if u in data[v]:
            del data[v][u]
            del incoming[u][v]

    @property
    def edge_count(self):
        return sum(len(neighbors) for neighbors in self._data.values())

    def add_node(self, u, neighbors=None):
        """Add node ``u`` and, optionally, its ``neighbors``."""
        if neighbors is None:
            neighbors = {}
        if u in self._data:
            del self[u]
        self._data[u] = neighbors
        for v, edge in neighbors.items():
            self._incoming[v][u] = edge
        return self._data[u]

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
                neighbors = reader(fp)
        else:
            neighbors = reader(from_)
        return cls(neighbors)

    def _write(self, writer, to):
        """Write to path or open file using specified writer."""
        if isinstance(to, str):
            with open(to, 'wb') as fp:
                writer(self._data, fp)
        else:
            writer(self._data, to)

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
