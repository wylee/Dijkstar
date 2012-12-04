###############################################################################
# Created 2004-12-28.
#
# Dijkstra/A* path-finding functions.
#
# Copyright (C) 2004-2007, 2012 Wyatt Baldwin. All rights reserved.
#
# Licensed under the MIT license.
#
#    http://www.opensource.org/licenses/mit-license.php
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###############################################################################
"""Dijkstra/A* path-finding functions."""
import heapq


class DijkstarError(Exception):
    """Base class for Dijkstar errors."""


class NoPathError(DijkstarError):
    """Raised when a path can't be found to a specified node."""


def find_path(graph, annex, s, d, cost_func=None, heuristic_func=None):
    """Find the shortest path from ``s`` to ``d`` in ``graph``.

    Returns ordered path data. For details, see
    :func:`extract_shortest_path_from_predecessor_list`.

    """
    predecessors, costs = single_source_shortest_paths(
        graph, annex, s, d, cost_func, heuristic_func)
    return extract_shortest_path_from_predecessor_list(predecessors, d)


def single_source_shortest_paths(graph, annex, s, d=None, cost_func=None,
                                 heuristic_func=None):
    """Find path from node ``s`` to all other nodes or just to ``d``.

    ``graph``
        v and u are vertices; e is an edge.

        {
            'nodes': {  # Adjacency matrix
                v: {u: e, ...},  # Vertex v goes to vertex u via edge e
                .
                .
                .
             },

             'edges': {  # Edge attributes
                 e: (cost, attr_a, attr_b, ...),  # Edge e's attributes
                 .
                 .
                 .
             }
        }

        Edge attribute lists _must_ contain the cost entry first; they
        may also contain other attributes of the edge. These other
        attributes can be used to determine a different cost for the
        edge if ``cost_func`` is given.

    ``annex``
        Another ``graph`` that can be used to augment ``graph`` without
        altering it.

    ``s``
        Start node.

    ``d``
        Destination node. If ``d`` is not specified, the algorithm is
        run normally (i.e., the paths from ``s`` to all reachable nodes
        are found). If ``d`` is specified, the algorithm is stopped when
        a path to ``d`` has been found.

    ``cost_func``
        A function to apply to each edge to modify its base cost.

    ``heuristic_func``
        A function to apply at each iteration to help the poor dumb
        machine try to move toward the destination instead of just any
        and every which way.

    return
        - Predecessor map {v => (u, e), ...}
        - Cost of path from ``s`` to all reached nodes {v => cost, ...}

    """
    # Current known costs of paths from s to all nodes that have been
    # reached so far
    costs = {s: 0}

    # Used with heapq to maintain a priority queue of nodes with known
    # costs from s
    open = [(0, s)]

    # Predecessor of each node that has shortest path from s
    predecessors = {}

    nodes, edges = graph['nodes'], graph['edges']
    h_nodes, h_edges = annex['nodes'], annex['edges']

    while open:
        # In the nodes remaining in the graph that have a known cost
        # from s, find the node, u, that currently has the shortest path
        # from s.
        cost_of_s_to_u, u = heapq.heappop(open)

        # Get the attributes of the segment crossed to get to u.
        try:
            prev_e_attrs = predecessors[u][2]
        except KeyError:
            prev_e_attrs = None

        # Get nodes adjacent to u...
        if u in h_nodes:
            A = h_nodes[u]
        else:
            try:
                A = nodes[u]
            except KeyError:
                # u has no outgoing edges
                continue

        # ...and explore the edges that connect u to those nodes,
        # updating the cost of the shortest paths to any or all of
        # those nodes as necessary. v is the node across the current
        # edge from u.
        for v in A:
            e = A[v]

            if e in h_edges:
                e_attrs = h_edges[e]
            else:
                e_attrs = edges[e]

            # Get the cost of the edge running from u to v
            try:
                cost_of_e = cost_func(v, e_attrs, prev_e_attrs)
            except TypeError:
                cost_of_e = e_attrs[0]

            # Cost of s to u plus the cost of u to v across e--this
            # is *a* cost from s to v that may or may not be less than
            # the current known cost to v
            cost_of_s_to_u_plus_cost_of_e = cost_of_s_to_u + cost_of_e

            # When there is a heuristic function, we use
            # a "guess-timated" cost, which is the normal cost plus
            # some other heuristic cost from v to d that is calculated
            # so as to keep us moving in the right direction (generally
            # more toward the goal instead of away from it).
            #try:
            #    cost_of_s_to_u_plus_cost_of_e += heuristic_func(e)
            #except TypeError:
            #    pass

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
                    predecessors[v] = (u, e, e_attrs)
            else:
                # No path to v had been found previously.
                costs[v] = cost_of_s_to_u_plus_cost_of_e
                predecessors[v] = (u, e, e_attrs)
                heapq.heappush(open, (cost_of_s_to_u_plus_cost_of_e, v))

            if v == d:
                return predecessors, costs

    if d is not None and d not in costs:
        raise NoPathError('Could not find a path from {0} to {1}'.format(s, d))

    return predecessors, costs


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
        predecessor_data = predecessors[u]
        e = predecessor_data[1]
        attrs = predecessor_data[2]
        nodes.append(u)
        edges.append(e)
        costs.append(attrs[0])
        u = predecessor_data[0]
    nodes.append(u)  # Start node
    nodes.reverse()
    edges.reverse()
    costs.reverse()
    total_cost = sum(costs)
    return nodes, edges, costs, total_cost
