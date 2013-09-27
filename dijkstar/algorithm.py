"""Dijkstra/A* path-finding functions."""
from heapq import heappush, heappop


class DijkstarError(Exception):
    """Base class for Dijkstar errors."""


class NoPathError(DijkstarError):
    """Raised when a path can't be found to a specified node."""


def find_path(graph, s, d, annex=None, cost_func=None, heuristic_func=None):
    """Find the shortest path from ``s`` to ``d`` in ``graph``.

    Returns ordered path data. For details, see
    :func:`extract_shortest_path_from_predecessor_list`.

    """
    predecessors = single_source_shortest_paths(
        graph, s, d, annex, cost_func, heuristic_func)
    return extract_shortest_path_from_predecessor_list(predecessors, d)


def single_source_shortest_paths(graph, s, d=None, annex=None, cost_func=None,
                                 heuristic_func=None):
    """Find path from node ``s`` to all other nodes or just to ``d``.

    ``graph``
        A simple adjacency matrix (see :class:`dijkstra.graph.Graph`).
        Other than the structure, no other assumptions are made about
        the types of the nodes or edges in the graph. As a simple
        special case, if ``cost_func`` isn't specified, edges will be
        assumed to be simple numeric values.

    ``s``
        Start node.

    ``d``
        Destination node. If ``d`` is not specified, the algorithm is
        run normally (i.e., the paths from ``s`` to all reachable nodes
        are found). If ``d`` is specified, the algorithm is stopped when
        a path to ``d`` has been found.

    ``annex``
        Another ``graph`` that can be used to augment ``graph`` without
        altering it.

    ``cost_func``
        A function to apply to each edge to modify its base cost. The
        arguments it will be passed are the current node, a neighbor of
        the current node, the edge that connects the current node to
        that neighbor, and the edge that was previously traversed to
        reach the current node.

    ``heuristic_func``
        A function to apply at each iteration to help the poor dumb
        machine try to move toward the destination instead of just any
        and every which way. It gets passed the same args as
        ``cost_func``.

    return
        - Predecessor map {v => (u, e, cost to traverse e), ...}

    """
    # Current known costs of paths from s to all nodes that have been
    # reached so far
    costs = {s: 0}

    # Used with heapq to maintain a priority queue of nodes with known
    # costs from s
    open = [(0, s)]

    # Predecessor of each node that has shortest path from s
    predecessors = {}

    destination_specified = d is not None

    if destination_specified:
        # Keep track of which incoming nodes ``d`` has been visited
        # from; when ``d`` has been visited from each of those nodes,
        # the shortest path to ``d`` will have been found.
        incoming_nodes = set()
        incoming_nodes.update(graph.incoming_nodes[d])
        if annex is not None:
            incoming_nodes.update(annex.incoming_nodes[d])

    while open:
        if destination_specified and not incoming_nodes:
            break

        # In the nodes remaining in the graph that have a known cost
        # from s, find the node, u, that currently has the shortest path
        # from s.
        cost_of_s_to_u, u = heappop(open)

        # The edge crossed to get to u
        prev_e = predecessors.get(u, None)

        # Get nodes adjacent to u...
        if annex and u in annex:
            neighbors = annex[u]
        else:
            try:
                neighbors = graph[u]
            except KeyError:
                # u has no outgoing edges
                continue

        # ...and explore the edges that connect u to those nodes,
        # updating the cost of the shortest paths to any or all of
        # those nodes as necessary. v is the node across the current
        # edge from u.
        for v in neighbors:
            e = neighbors[v]

            if destination_specified and v == d:
                # Record that d has been visited from u
                incoming_nodes.remove(u)

            # Get the cost of the edge running from u to v
            if cost_func:
                cost_of_e = cost_func(u, v, e, prev_e)
            else:
                cost_of_e = e

            # Cost of s to u plus the cost of u to v across e--this
            # is *a* cost from s to v that may or may not be less than
            # the current known cost to v
            cost_of_s_to_u_plus_cost_of_e = cost_of_s_to_u + cost_of_e

            # When there is a heuristic function, we use
            # a "guess-timated" cost, which is the normal cost plus
            # some other heuristic cost from v to d that is calculated
            # so as to keep us moving in the right direction (generally
            # more toward the goal instead of away from it).
            if heuristic_func:
                additional_cost = heuristic_func(u, v, e, prev_e)
                cost_of_s_to_u_plus_cost_of_e += additional_cost

            if v in costs:
                # If the current known cost from s to v is greater than
                # the cost of the path that was just found (cost of s to
                # u plus cost of u to v across e), update v's cost in
                # the cost list and update v's predecessor in the
                # predecessor list (it's now u)
                if costs[v] > cost_of_s_to_u_plus_cost_of_e:
                    costs[v] = cost_of_s_to_u_plus_cost_of_e
                    # u is v's predecessor node. e is the ID of the edge
                    # running from u to v on the shortest known path
                    # from s to v. We include the edge's other
                    # attributes too.
                    predecessors[v] = (u, e, cost_of_e)
            else:
                # No path to v had been found previously.
                costs[v] = cost_of_s_to_u_plus_cost_of_e
                predecessors[v] = (u, e, cost_of_e)
                heappush(open, (cost_of_s_to_u_plus_cost_of_e, v))

    if destination_specified and d not in costs:
        raise NoPathError('Could not find a path from {0} to {1}'.format(s, d))

    return predecessors


def extract_shortest_path_from_predecessor_list(predecessors, d):
    """Extract ordered lists of nodes, edges, costs from predecessor list.

    ``predecessors``
        Predecessor list {u: (v, e), ...} u's predecessor is v via e

    ``d``
        Destination node

    return
        - The nodes on the shortest path to ``d``
        - The edges on the shortest path to ``d``
        - The costs of the edges on the shortest path to ``d``
        - The total cost of the path

    """
    nodes = []  # Node IDs on the shortest path from s to d
    edges = []  # Edge IDs on the shortest path from s to d
    costs = []  # Costs of the edges on the shortest path from s to d
    u = d
    while u in predecessors:
        v, e, cost = predecessors[u]
        nodes.append(u)
        edges.append(e)
        costs.append(cost)
        u = v
    nodes.append(u)  # Start node
    nodes.reverse()
    edges.reverse()
    costs.reverse()
    total_cost = sum(costs)
    return nodes, edges, costs, total_cost
