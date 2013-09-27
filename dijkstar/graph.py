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
        """Get neighbors of node ``u``."""
        return self._data[u]

    def __setitem__(self, u, neighbors):
        """Set neighbors for node ``u``.

        This completely replaces ``u``'s current neighbors if ``u`` is
        already present.

        Also clears ``u``'s incoming list and updates the incoming list
        for each of the nodes in ``neighbors`` to include ``u``.

        To add an edge to an existing node, use :meth:`add_edge`
        instead.

        ``neighbors``
            A mapping of the nodes adjacent to ``u`` and the edges that
            connect ``u`` to those nodes: {v1: e1, v2: e2, ...}.

        """
        if u in self:
            del self[u]
        self._data[u] = neighbors
        for v, edge in neighbors.items():
            self._incoming[v][u] = edge

    def __delitem__(self, u):
        """Remove node ``u``."""
        del self._data[u]
        del self._incoming[u]
        for incoming in self._incoming.values():
            if u in incoming:
                del incoming[u]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def add_edge(self, u, v, edge=None):
        """Add an ``edge`` from ``u`` to ``v``."""
        if u in self:
            neighbors = self[u]
            neighbors[v] = edge
            self._incoming[v][u] = edge
        else:
            self[u] = {v: edge}

    def add_node(self, u, neighbors=None):
        """Add the node ``u``.

        This simply delegates to :meth:`__setitem__`. The only
        difference between this and that is that ``neighbors`` isn't
        required when calling this.

        """
        self[u] = neighbors if neighbors is not None else {}

    def get_incoming(self, v):
        return self._incoming[v]

    @classmethod
    def _load(cls, loader, path):
        with open(path, 'rb') as loadfile:
            neighbors = loader(loadfile)
        return cls(neighbors)

    def _dump(self, dumper, path):
        with open(path, 'wb') as dumpfile:
            dumper(self._data, dumpfile)

    @classmethod
    def load(cls, path):
        """Load pickled graph from ``path``."""
        return cls._load(pickle.load, path)

    def dump(self, path):
        """Dump pickled graph to ``path``."""
        self._dump(pickle.dump, path)

    @classmethod
    def unmarshal(cls, path):
        """Read graph from disk using marshal.

        Marshalling is quite a bit faster than pickling, but only the
        following types are supported: booleans, integers, long
        integers, floating point numbers, complex numbers, strings,
        Unicode objects, tuples, lists, sets, frozensets, dictionaries,
        and code objects.

        The method names `unmarshal` and `marshal` were chosen based on
        this note in the standard library documentation: "Strictly
        speaking, 'to marshal' means to convert some data from internal
        to external form and 'unmarshalling' for the reverse process."

        """
        return cls._load(marshal.load, path)

    def marshal(self, path):
        """Write graph to disk using marshal.

        See note in :meth:`unmarshal`.

        """
        self._dump(marshal.dump, path)
