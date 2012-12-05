Dijkstar
++++++++

Dijkstar is an implementation of Dijkstra's single-source shortest-paths
algorithm. If a destination node is given, the algorithm halts when that
node is reached; otherwise it continues until paths from the source node
to all other nodes are found.

Accepts an optional cost (or "weight") function that will be called on
every iteration.

Also accepts an optional heuristic function that is used to push the
algorithm toward a destination instead of fanning out in every
direction. Using such a heuristic function converts Dijkstra to A* (and
this is where the name "Dijkstar" comes from).

Performance is decent on a graph with 100,000+ nodes. Runs in around .5
seconds on average .

Example::

    >>> from dijkstar import Graph, find_path
    >>> graph = Graph()
    >>> graph.add_edge(1, 2, {'cost': 1})
    >>> graph.add_edge(2, 3, {'cost': 2})
    >>> cost_func = lambda u, v, e, prev_e: e['cost']
    >>> find_path(graph, 1, 2, cost_func=cost_func)

The cost function is passed the current node (u), a neighbor (v) of the
current node, the edge that connects u to v, and the edge that was
traversed previously to get to the current node. In the example above,
the cost function simply returns the edge's `cost`.

The graph can be saved to disk (pickled) like so::

    >>> graph.dump(path)

And read back like this (load is a classmethod that returns a
populated Graph instance)::

    >>> Graph.load(path)
