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
seconds on average.

Example::

    >>> from dijkstar import Graph, find_path
    >>> graph = Graph()
    >>> graph.add_edge(1, 2, 110)
    >>> graph.add_edge(2, 3, 125)
    >>> graph.add_edge(3, 4, 108)
    >>> find_path(graph, 1, 4)
    PathInfo(
        nodes=[1, 2, 3, 4],
        edges=[110, 125, 108],
        costs=[110, 125, 108],
        total_cost=343)

In this example, the edges are just simple numeric values--110, 125,
108--that could represent lengths, such as the length of a street
segment between two intersections. ``find_path`` will use these values
directly as costs.

Example with cost function::

    >>> from dijkstar import Graph, find_path
    >>> graph = Graph()
    >>> graph.add_edge(1, 2, (110, 'Main Street'))
    >>> graph.add_edge(2, 3, (125, 'Main Street'))
    >>> graph.add_edge(3, 4, (108, '1st Street'))
    >>> def cost_func(u, v, edge, prev_edge):
    ...     length, name = edge
    ...     if prev_edge:
    ...         prev_name = prev_edge[1]
    ...     else:
    ...         prev_name = None
    ...     cost = length
    ...     if name != prev_name:
    ...         cost += 10
    ...     return cost
    ...
    >>> find_path(graph, 1, 4, cost_func=cost_func)
    PathInfo(
        nodes=[1, 2, 3, 4],
        edges=[(110, 'Main Street'), (125, 'Main Street'), (108, '1st Street')],
        costs=[120, 125, 118],
        total_cost=363)

The cost function is passed the current node (u), a neighbor (v) of the
current node, the edge that connects u to v, and the edge that was
traversed previously to get to the current node.

A cost function is most useful when computing costs dynamically. If
costs in your graph are fixed, a cost function will only add unnecessary
overhead. In the example above, a penalty is added when the street name
changes.

When using a cost function, one recommendation is to compute a base cost when
possible. For example, for a graph that represents a street network, the base
cost for each street segment (edge) could be the length of the segment
multiplied by the speed limit. There are two advantages to this: the size of
the graph will be smaller and the cost function will be doing less work, which
may improve performance.

Graph Export & Import
=====================

The graph can be saved to disk (pickled) like so::

    >>> graph.dump(path)

And read back like this (load is a classmethod that returns a
populated Graph instance)::

    >>> Graph.load(path)
