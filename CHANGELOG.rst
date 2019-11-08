2.5.0 (unreleased)
------------------

- Started supporting for Python 3.7 and 3.8 (no code changes required).
- Added support for undirected graphs. The implementation is simple. An
  undirected graph is just a directed graph that automatically adds the
  edge `(v, u)` when `(u, v)` is added and automatically removes
  `(v, u)` when `(u, v)` is removed.
- Added several new `Graph` methods and properties:
  - `get_data()` -> Get underlying data dict
  - `node_count` -> Return the number of nodes in the graph
  - `get_node()` -> Get a node
  - `remove_node()` -> Remove a node
  - `edge_count` -> Return the number of edges in the graph
  - `get_edge()` -> Get an edge
  - `remove_edge()` -> Remove an edge
  - `subgraph()` -> Get a subgraph with the specified nodes
  - `guess_load()` -> Load any supported graph type from file
  - `__eq__()` -> Graph equal to other graph? (compares data dicts)
  - `__repr__()` -> Graph representation (repr of data dict)
- Made `Graph`'s mapping interface methods (e.g., `__setitem__()`) call
  the corresponding method (e.g., `add_node()`) instead of vice versa.
- Made `Graph.add_node()` return the added node.
- Made `Graph.add_edge()` return the added edge.
- Fixed `Graph.add_edge(u, v)` so it *always* updates `v`'s incoming
  list, both when `u` is already in the graph and when it's not.
- When a node's incoming list becomes empty, delete it (i.e., the node's
  entry in the incoming list, not the node).
- In `single_source_shortest_paths()`, operate on the underlying data
  dict instead of going through `Graph`'s mapping interface. This should
  improve performance (or, at least, that's the intent).
- Added `debug` flag to `single_source_shortest_paths()`. When set,
  additional debugging info is returned along with the path info.
- Improved README, esp. wrt. path-finding examples and cost functions.
- Added and improved docstrings.
- Added more tests.
- Added Travis CI config.
- Started using setuptools instead of distutils for packaging.
- Added `dijkstar.__version__`.
- Improved some other packaging-related stuff.

2.4.0 (2018-01-01)
------------------

- Added option of passing an open file to `Graph` read/write methods (in
  addition to being able to pass a path name as before).


2.3 (2017-11-09)
----------------

- Added incremental count to priority queue entries in
  `algorithm.single_source_shortest_paths()`. The reason for this is
  given in the standard library docs for the `heapq` module: "The entry
  count serves as a tie-breaker so that two [items] with the same
  priority are returned in the order they were added. And since no two
  entry counts are the same, the tuple comparison will never attempt to
  directly compare two tasks."

- Updated project metaata:
  - Changed project status from alpha to beta
  - Updated author name & email
  - Removed support for Python 2.6
  - Added support for Python 3.4, 3.5, and 3.6

- Added flake8 config and removed lint

- Added tox config


2.2 (2014-03-31)
----------------

- Bugfix: Pass previous edge to cost & heuristic functions instead of
  the whole predecessor tuple (node, edge, cost).
- Add a test that passes a cost function to `find_path()`.
- Improve package metadata.


2.1 (2014-02-01)
----------------

- Made Python 3 compatible (required one tiny change in test code).
- Added a proper version of break-early.
- Made Graph implement the MutableMapping interface (while keeping the
  rest of its public API the same).
- Keep track of each node's incoming nodes (not sure this is useful
  though).
- Improved single_source_shortest_paths() (see 782f1e23).
  - Use "visited" and "reached" terminology.
  - Don't backtrack to already-visited nodes.
  - Update the best cost to a node every time it's reached.
  - Simplify and remove redundancy.
- Improved docstrings and comments throughout.
- Add more tests.


2.0 (2013-03-26)
----------------

- Assume Buildout 2.0.
- Removed naive break-early logic (see r666129f3eed8).


2.0b3 (2012-12-06)
------------------

- Tried to improve performance slightly by importing heappush and
  heappop and using them directly in the single_source_shortest_paths
  inner loop (instead of doing, e.g., heapq.heappush).

- The Graph loaded by pickle.load is now returned directly. Before,
  Graph.load was needlessly creating a new Graph initialized with the
  Graph returned from pickle.load. Doesn't affect performance in any
  noticeable way.

- Added marshal and unmarshal methods to Graph. These are similar to the
  dump and load methods but use the standard library marshal module
  instead of pickle. Reading and writing using marshal is significantly
  faster than pickle (reading from disk was about three times faster in
  my tests), but marshal supports only built-in types.


2.0b2 (2012-12-04)
------------------

Fixed broken package config. setup() call was missing packages option,
so no packages were added to the distribution. Also added a MANIFEST.in.


2.0b1 (2012-12-04)
------------------

- Cleaned up a lot of stuff--made more readable, fixed formatting,
  fixed single letter variable names, improved comments, cleaned up
  setup.py, added README, added CHANGELOG

- Added a module for tests; only one test so far, but that's better than
  nothing!

- Changed expected graph structure to simple adjacency matrix:
  {u: {v: edge, ...}, ...}

- Added Graph type to make construction and de/serialization of graphs
  easier; it also serves as a template for custom graph types by
  encapsulating the expected graph structure

- Restructured package so algorithmic code is in separate module (not
  __init__) and __init__ just exports the public API

- Made the ``annex`` arg to find_path() and
  single_source_shortest_paths() optional

- Pass the current node as the first arg to cost functions

- Reenabled heuristic function (it was commented out); pass it the same
  args as cost function

- Return computed edge costs from single_source_shortest_paths as part
  of the predecessor list

- Return only the predecessor list from single_source_shortest_paths;
  don't return the dictionary of total costs of s to all v reached
  (XXX: Would it maybe be useful to return this? Especially for the case
  where no destination node is specified?)

- Removed infinity wonkiness from single_source_shortest_paths (see
  d89a851 for details; basically, sys.infinity was being used
  unnecessarily as a special sentinel value)


History
-------

Dijkstar was originally written in December of 2004, and hadn't changed
much between then and just recently. It was spun off from the byCycle
project (bycycle.org) in 2007.

For years I had been planning to switch byCycle over to NetworkX, but
I was busy with other things and byCycle languished. I found some free
time recently to make the switch, but I found that NetworkX didn't fully
serve my needs. (I also found that it takes a similar approach in its
graph implementations: they're just dictionaries.)

The feature I need that is missing from NetworkX is the ability to pass
a cost function into the path finding function (this is something that
byCycle relies on). NetworkX only works with precomputed costs.

I decided to go ahead and polish up Dijkstar and release it as possible
lightweight alternative to NetworkX for simple use cases.

I was inspired by NetworkX and added a simple Graph class that has
a stripped down version of NetorkX's graph API (add_edge, add_node).
I also added utility methods for dumping graphs to and loading them from
disk (using pickle).
