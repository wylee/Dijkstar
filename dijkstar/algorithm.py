"""Dijkstra/A* path-finding functions."""
from collections import namedtuple
from heapq import heappush, heappop
from inspect import ismethod
from itertools import count


PathInfo = namedtuple('PathInfo', ('nodes', 'edges', 'costs', 'total_cost'))
"""Info for shortest path found between start and destination nodes.

``nodes``
    Nodes comprising the shortest path.

``edges``
    Edges comprising the shortest path.

``costs``
    Cost to traverse each edge in ``edges``. When a cost function is
    passed to :func:`find_path`, these will be *computed* costs, which
    may or not correspond to any real world value such as edge length
    (depends on the cost function and how it computes costs). When a
    cost function isn't passed, this will be equal to ``edges``.

``total_cost``
    This is simply the sum of ``costs``. When a cost function is passed
    to :func:`find_path`, this will be the sum of the *computed* costs,
    which may not correspond to any real world value. When a cost
    function isn't used, this will be equal to ``sum(edges)``.

"""


DebugInfo = namedtuple('DebugInfo', 'costs visited')


class DijkstarError(Exception):
    """Base class for Dijkstar errors."""


class NoPathError(DijkstarError):
    """Raised when a path can't be found to a specified node."""


def find_path(graph, s, d, annex=None, cost_func=None, heuristic_func=None):
    """Find the shortest path from ``s`` to ``d`` in ``graph``.

    This is a wrapper around :func:`single_source_shortest_paths` that
    extracts path info from the the predecessor list. Look there for a
    description of the args.

    Returns
        A :class:`PathInfo` object.

    """
    predecessors = single_source_shortest_paths(
        graph, s, d, annex, cost_func, heuristic_func)
    return extract_shortest_path_from_predecessor_list(predecessors, d)


def single_source_shortest_paths(graph, s, d=None, annex=None, cost_func=None,
                                 heuristic_func=None, debug=False):
    """Find path from node ``s`` to all other nodes or just to ``d``.

    ``graph``
        An adjacency list that's structured as a dict of dicts (see
        :class:`dijkstra.graph.Graph`). Other than the structure, no
        other assumptions are made about the types of the nodes or edges
        in the graph. If ``cost_func`` isn't specified, edges will be
        assumed to be values that can be compared directly (e.g.,
        numbers, or any other comparable type).

    ``s``
        Start node.

    ``d``
        Destination node. If ``d`` is not specified, the algorithm is
        run normally (i.e., the paths from ``s`` to all reachable nodes
        are found). If ``d`` is specified, the algorithm is stopped when
        a path to ``d`` has been found.

    ``annex``
        Another graph that can be used to augment ``graph`` without
        altering it.

    ``cost_func``
        A function to apply to each edge to modify its base cost. The
        arguments it will be passed are the current node, a neighbor of
        the current node, the edge that connects the current node to
        that neighbor, and the edge that was previously traversed to
        reach the current node.

    ``heuristic_func``
        A function to apply at each iteration to guide the algorithm
        toward the destination (typically) instead of fanning out. It
        gets passed the same args as ``cost_func``.

    ``debug``
        If set, return additional info that may be useful for debugging.

    Returns
        A predecessor map with the following form::

            {v => (u, e, cost from v to u over e), ...}

        If ``debug`` is set, additional debugging info will be returned
        also. Currently, this info includes costs from ``s`` to reached
        nodes and the set of visited nodes.

    """
    # Operate on the underlying data dict to potentially improve
    # performance.
    if ismethod(getattr(graph, 'get_data', None)):
        graph = graph.get_data()
    if ismethod(getattr(annex, 'get_data', None)):
        annex = annex.get_data()

    counter = count()

    # Current known costs of paths from s to all nodes that have been
    # reached so far. Note that "reached" is not the same as "visited".
    costs = {s: 0}

    # Predecessor map for each node that has been reached from ``s``.
    # Keys are nodes that have been reached; values are tuples of
    # predecessor node, edge traversed to reach predecessor node, and
    # cost to traverse the edge from the predecessor node to the reached
    # node.
    predecessors = {s: (None, None, None)}

    # A priority queue of nodes with known costs from s. The nodes in
    # this queue are candidates for visitation. Nodes are added to this
    # queue when they are reached (but only if they have not already
    # been visited).
    visit_queue = [(0, next(counter), s)]

    # Nodes that have been visited. Once a node has been visited, it
    # won't be visited again. Note that in this context "visited" means
    # a node has been selected as having the lowest known cost (and it
    # must have been "reached" to be selected).
    visited = set()

    while visit_queue:
        # In the nodes remaining in the graph that have a known cost
        # from s, find the node, u, that currently has the shortest path
        # from s.
        cost_of_s_to_u, _, u = heappop(visit_queue)

        if u == d:
            break

        if u in visited:
            # This will happen when u has been reached from multiple
            # nodes before being visited (because multiple entries for
            # u will have been added to the visit queue).
            continue

        visited.add(u)

        if annex and u in annex:
            neighbors = annex[u]
        else:
            neighbors = graph[u] if u in graph else None

        if not neighbors:
            # u has no outgoing edges
            continue

        # The edge crossed to get to u
        prev_e = predecessors[u][1]

        # Check each of u's neighboring nodes to see if we can update
        # its cost by reaching it from u.
        for v in neighbors:
            # Don't backtrack to nodes that have already been visited.
            if v in visited:
                continue

            e = neighbors[v]

            # Get the cost of the edge running from u to v.
            cost_of_e = cost_func(u, v, e, prev_e) if cost_func else e

            # Cost of s to u plus the cost of u to v across e--this
            # is *a* cost from s to v that may or may not be less than
            # the current known cost to v.
            cost_of_s_to_u_plus_cost_of_e = cost_of_s_to_u + cost_of_e

            # When there is a heuristic function, we use a
            # "guess-timated" cost, which is the normal cost plus some
            # other heuristic cost from v to d that is calculated so as
            # to keep us moving in the right direction (generally more
            # toward the goal instead of away from it).
            if heuristic_func:
                additional_cost = heuristic_func(u, v, e, prev_e)
                cost_of_s_to_u_plus_cost_of_e += additional_cost

            if v not in costs or costs[v] > cost_of_s_to_u_plus_cost_of_e:
                # If the current known cost from s to v is greater than
                # the cost of the path that was just found (cost of s to
                # u plus cost of u to v across e), update v's cost in
                # the cost list and update v's predecessor in the
                # predecessor list (it's now u). Note that if ``v`` is
                # not present in the ``costs`` list, its current cost
                # is considered to be infinity.
                costs[v] = cost_of_s_to_u_plus_cost_of_e
                predecessors[v] = (u, e, cost_of_e)
                heappush(visit_queue, (cost_of_s_to_u_plus_cost_of_e, next(counter), v))

    if d is not None and d not in costs:
        raise NoPathError('Could not find a path from {0} to {1}'.format(s, d))

    if debug:
        return predecessors, DebugInfo(costs, visited)

    return predecessors


def extract_shortest_path_from_predecessor_list(predecessors, d):
    """Extract ordered lists of nodes, edges, costs from predecessor list.

    ``predecessors``
        Predecessor list {u: (v, e), ...} u's predecessor is v via e

    ``d``
        Destination node

    Returns
        A :class:`PathInfo` object.

    """
    nodes = [d]  # Nodes on the shortest path from s to d
    edges = []   # Edges on the shortest path from s to d
    costs = []   # Costs of the edges on the shortest path from s to d
    u, e, cost = predecessors[d]
    while u is not None:
        # u is the node from which v was reached, e is the edge
        # traversed to reach v from u, and cost is the cost of u to
        # v over e. (Note that v is implicit--it's the previous u).
        nodes.append(u)
        edges.append(e)
        costs.append(cost)
        u, e, cost = predecessors[u]
    nodes.reverse()
    edges.reverse()
    costs.reverse()
    total_cost = sum(costs)
    return PathInfo(nodes, edges, costs, total_cost)
