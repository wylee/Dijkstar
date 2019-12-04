# Dijkstar

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

Example:

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
segment between two intersections. `find_path` will use these values
directly as costs.

Example with cost function:

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

When using a cost function, one recommendation is to compute a base cost
when possible. For example, for a graph that represents a street
network, the base cost for each street segment (edge) could be the
length of the segment multiplied by the speed limit. There are two
advantages to this: the size of the graph will be smaller and the cost
function will be doing less work, which may improve performance.

## Graph Export & Import

The graph can be saved to disk (pickled) like so:

    >>> graph.dump(path)

And read back like this (load is a classmethod that returns a populated
Graph instance):

    >>> Graph.load(path)

## Server

Dijkstar comes with a simple, standalone, web-based graph server that's
built on top of [Starlette](https://www.starlette.io/) and
[Uvicorn](https://www.uvicorn.org/). It can be installed with pip:

    pip install Dijkstar[server]

This installs additional libraries as well as the `dijkstar serve`
console script. The server can be run like so:

    dijkstar serve

This runs `uvicorn` on `127.0.0.1:8000` with an empty graph.

A previously-saved graph can be loaded from disk like so:

    dijkstar serve -g path/to/graph

### Server Configuration

The server is configured via environment variables following the same
[12-factor pattern as Starlette](https://www.starlette.io/config/).
These can be set in the following ways, in order of precedence:

- Options passed to `dijkstar serve`, which will overwrite existing
  environment variables.
- Environment variables set in the usual way (e.g., via the shell).
- Variables set in an env file, which will be added to the environment
  if not already present. The default env file is `./.env` (relative
  to the server's PWD).

The environment variables affecting the server correspond to the
settings in the `dijkstar.server.conf` module (with names upper-cased).

TODO: Document environment variables here.


### Road Map/Planned Features

- [x] Console script to run server
- [x] Configuration via env file
- [x] Configuration console script options
- [x] Load graph from file on startup
- [ ] Endpoints
  - [ ] HTML home page listing available endpoints
  - [x] /graph-info -> Basic graph info
  - [x] /load-graph -> Load a new graph (from file or data)
  - [x] /reload-graph -> Reload the current graph file
  - [ ] /add-edge -> Add edge to graph
  - [x] /get-edge -> Get edge from graph
  - [ ] /add-node -> Add node to graph
  - [x] /get-node -> Get node from graph
  - [x] /find-path -> Find path between nodes in graph
- [ ] Client wrapping server API calls
  - [x] Graph info
  - [x] Load graph
  - [x] Reload graph
  - [ ] Add edge
  - [x] Get edge
  - [ ] Add node
  - [x] Get node
  - [x] Find path
- [ ] Auth?

### Clients

Any HTTP client can be used to make requests to the server, such as
`fetch` in the browser or `curl` on the command line. For example,
`fetch` can be used to interact with a graph directly from a web app:

    const response = await fetch('http://localhost:8000/graph-info')
    const info = await response.json();

Dijkstar also includes a client that can be used to make requests
conveniently from Python code:

    from dijkstar.server.client import Client
    client = Client()  # Uses the default base URL http://localhost:8000
    info = client.graph_info()

This is intended for use in scripts, back end web services, and the
like. Here's an example of using the client in a Django-style view:

    def find_path_view(request):
        path = client.find_path(1, 2)
        # Process the path. For example, you might retrieve edges from
        # the database here.
        edges = Edge.objects.filter(id__in=path['edges'])
        edges = [{'id': edge.id, 'name': edge.name} for edge in edges]
        return JsonResponse(edges)
