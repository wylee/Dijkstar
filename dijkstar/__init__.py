###############################################################################
# $Id$
# Created 2004-12-28.
#
# Dijkstra/A* path-finding functions.
#
# Copyright (C) 2004-2007, Wyatt Baldwin. All rights reserved.
#
# Licensed under the MIT license.
#
#    http://www.opensource.org/licenses/mit-license.php
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################
"""Dijkstra/A* path-finding functions."""
import heapq


class DijkstarError(Exception):
    """Base class for Dijkstar errors."""

class NoPathError(DijkstarError):
    """Error raised when a path can't be found to a given node, ``d``."""


def single_source_shortest_paths(G, H, s, d=None, weight_func=None,
                                 heuristic_func=None):
    """Find path from node ``s`` to all other nodes, or just to ``d``.

    ``G``
        Graph of sorts. "v" or "u" is a vertex; "e" is an edge.

        {
            'nodes': {  # Adjacency matrix
                v: {u: e, ...},  # Vertex v goes to vertex u via edge e
                .
                .
                .
             },

             'edges': {  # Edge attributes
                 e: (weight, attr_a, attr_b, ...),  # Edge e's attributes
                 .
                 .
                 .
             }
        }

        Edge attribute lists _must_ contain the weight entry first; they may
        also contain other attributes of the edge. These other attributes can
        be used to determine a different weight for the edge.

    ``H``
        "Annex" to ``G``; this is a graph just like ``G`` that can be used to
        augment ``G`` without altering it

    ``s``
        Start node ID

    ``d``
        Destination node ID. If ``d`` is None (default) the algorithm is run
        normally. If ``d`` has a value, the algorithm is stopped when a path
        to ``d`` has been found.

    ``weight_func``
        Function to apply to each edge to modify its base weight.

    ``heuristic_func``
        A function to apply at each iteration to help the poor dumb machine
        try to move toward the destination instead of just any and every which
        way.

    return
        * Predecessor mapping {v => (u, e), ...}
        * Weights of paths from node ``s`` to all reached nodes {v => w, ...}

    """
    # weights of shortest paths from s to all v (ID of v => w)
    W = {s: 0}
    # partially sorted list of nodes w/ known weights from s
    open = [(0, s)]
    # predecessor of each node that has shortest path from s
    P = {}

    nodes, edges = G['nodes'], G['edges']
    h_nodes, h_edges = H['nodes'], H['edges']

    while open:
        # In the nodes remaining in G that have a known weight from s,
        # find the node, u, that currently has the shortest path from s
        w_of_s_to_u, u = heapq.heappop(open)

        # Get the attributes of the segment crossed to get to u
        try:
            prev_e_attrs = P[u][2]
        except KeyError:
            prev_e_attrs = None

        # Get nodes adjacent to u...
        if u in h_nodes:
            A = h_nodes[u]
        else:
            try:
                A = nodes[u]
            except KeyError:
                # We'll get here upon reaching a node with no outgoing edges
                continue

        # ...and explore the edges that connect u to those nodes, updating
        # the weight of the shortest paths to any or all of those nodes as
        # necessary. v is the node across the current edge from u.
        for v in A:
            e = A[v]

            if e in h_edges:
                e_attrs = h_edges[e]
            else:
                e_attrs = edges[e]

            # Get the weight of the edge running from u to v
            try:
                w_of_e = weight_func(v, e_attrs, prev_e_attrs)
            except TypeError:
                w_of_e = e_attrs[0]

            # Weight of s to u plus the weight of u to v across e--this is *a*
            # weight from s to v that may or may not be less than the current
            # known weight to v
            w_of_s_to_u_plus_w_of_e = w_of_s_to_u + w_of_e

            # When there is a heuristic function, we use a "guess-timated"
            # weight, which is the normal weight plus some other heuristic
            # weight from v to d that is calculated so as to keep us moving
            # in the right direction (generally more toward the goal instead
            # of away from it).
            #try:
            #    w_of_s_to_u_plus_w_of_e += heuristic_func(e)
            #except TypeError:
            #    pass

            if v in W:
                # If the current known weight from s to v is greater
                # than the weight of the path that was just found
                # (weight of s to u plus weight of u to v across e),
                # update v's weight in the weight list and update v's
                # predecessor in the predecessor list (it's now u)
                if W[v] > w_of_s_to_u_plus_w_of_e:
                    W[v] = w_of_s_to_u_plus_w_of_e
                    # u is v's predecessor node. e is the ID of the edge
                    # running from u to v on the shortest known path
                    # from s to v. We include the edge's other
                    # attributes too.
                    P[v] = (u, e, e_attrs)
            else:
                # No path to v had been found previously.
                W[v] = w_of_s_to_u_plus_w_of_e
                P[v] = (u, e, e_attrs)
                heapq.heappush(open, (w_of_s_to_u_plus_w_of_e, v))

            # If a destination node was specified and we reached it, we're done
            if v == d:
                open = None
                break

    if d is not None and d not in W:
        raise NoPathError('Could not find a path from node %s to node %s' %
                          (s, d))

    return P, W


def extract_shortest_path_from_predecessor_list(P, d):
    """Extract ordered lists of nodes, edges, weights from predecessor list.

    ``P``
        Predecessor list {u: (v, e), ...} u's predecessor is v via e

    ``d``
        Destination node ID

    return
        * The node IDs on the shortest path from origin to ``d``
        * The edge IDs on the shortest path from origin to ``d``
        * The weights of the edges on the shortest path from origin to ``d``
        * The total weight of the path

    """
    V = []  # Node IDs on the shortest path from s to d
    E = []  # Edge IDs on the shortest path from s to d
    W = []  # Weights of the edges on the shortest path from s to d
    u = d
    while u in P:
        predecessor_data = P[u]
        e = predecessor_data[1]
        attrs = predecessor_data[2]
        V.append(u)
        E.append(e)
        W.append(attrs[0])
        u = predecessor_data[0]
    V.append(u)  # Start node
    V.reverse(); E.reverse(); W.reverse()
    w = sum(W)
    return V, E, W, w


def find_path(G, H, s, d, weight_func=None, heuristic_func=None):
    """Find the shortest path from ``s`` to ``d`` in ``G``.

    This function just combines finding the predecessor list with extracting
    the node IDs from that list in the proper (path) order, 'cause what you
    want is probably that ordered list.

    return
        * The node IDs on the shortest path from origin to ``d``
        * The edge IDs on the shortest path from origin to ``d``
        * The weights of the edges on the shortest path from origin to ``d``
        * The total weight of the path

    """
    P, W = single_source_shortest_paths(G, H, s, d, weight_func,heuristic_func)
    return extract_shortest_path_from_predecessor_list(P, d)
