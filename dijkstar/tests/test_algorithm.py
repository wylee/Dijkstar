import unittest

from dijkstar import find_path, NoPathError, Graph
from dijkstar.algorithm import single_source_shortest_paths


class Tests(unittest.TestCase):

    def setUp(self):
        self.graph1 = Graph({
            1: {2: 1, 3: 2},
            2: {1: 1, 4: 2, 5: 2},
            3: {4: 2},
            4: {2: 2, 3: 2, 5: 1},
            5: {2: 2, 4: 1},
        })

        self.graph2 = Graph({
            'a': {'b': 10, 'd': 1},
            'b': {'a': 1, 'c': 2, 'e': 3},
            'c': {'b': 1, 'f': 2},
            'd': {'a': 1, 'e': 2, 'g': 3},
            'e': {'b': 1, 'd': 2, 'f': 3, 'h': 4},
            'f': {'c': 1, 'e': 2, 'i': 3},
            'g': {'d': 1, 'h': 2},
            'h': {'e': 1, 'g': 2, 'i': 3},
            'i': {'f': 1, 'h': 2}
        })

    @property
    def graph3(self):
        graph = Graph({
            'a': {'b': 10, 'c': 100, 'd': 1},
            'b': {'c': 10},
            'd': {'b': 1, 'e': 1},
            'e': {'f': 1},
        })

        graph.add_node('f', {'c': 1})
        graph['f'] = {'c': 1}

        graph.add_edge('f', 'c', 1)
        graph.add_edge('g', 'b', 1)

        nodes = list(graph)
        nodes.sort()
        self.assertEqual(nodes, ['a', 'b', 'd', 'e', 'f', 'g'])

        incoming = graph.get_incoming('c')
        incoming_nodes = list(incoming.keys())
        incoming_nodes.sort()
        self.assertEqual(incoming_nodes, ['a', 'b', 'f'])

        return graph

    def test_find_path_1(self):
        result = find_path(self.graph1, 1, 4)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1, 2, 4])
        self.assertEqual(edges, [1, 2])
        self.assertEqual(costs, [1, 2])
        self.assertEqual(total_cost, 3)

    def test_find_path_with_annex(self):
        annex = Graph({1: {2: 1, 3: 0.5}})
        result = find_path(self.graph1, 1, 4, annex=annex)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1, 3, 4])
        self.assertEqual(edges, [0.5, 2])
        self.assertEqual(costs, [0.5, 2])
        self.assertEqual(total_cost, 2.5)

    def test_path_with_cost_func(self):
        graph = {
            'a': {'b': (1, 10, 'A'), 'c': (1.5, 2, 'C')},
            'b': {'c': (1, 2, 'B'), 'd': (1, 10, 'A')},
            'c': {'b': (1, 3, 'B'), 'd': (1.5, 2, 'D')},
        }

        def cost_func(u, v, e, prev_e):
            cost = e[0]
            cost *= e[1]
            if prev_e is not None and e[2] != prev_e[2]:
                cost *= 1.25
            return cost

        result = find_path(graph, 'a', 'd', cost_func=cost_func)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, ['a', 'c', 'd'])

    def test_find_path_with_heuristic(self):
        def heuristic(u, v, e, prev_e):
            cost = u + 1 if v == 2 else 0
            if e != prev_e:
                cost += 1
            return cost
        result = find_path(self.graph1, 1, 4, heuristic_func=heuristic)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1, 3, 4])
        self.assertEqual(edges, [2, 2])
        self.assertEqual(costs, edges)
        self.assertEqual(total_cost, 4)

    def test_find_path_2(self):
        path = find_path(self.graph2, 'a', 'i')[0]
        self.assertEqual(path, ['a', 'd', 'e', 'f', 'i'])

    def test_find_path_3(self):
        path = find_path(self.graph3, 'a', 'c')[0]
        self.assertEqual(path, ['a', 'd', 'e', 'f', 'c'])

    def test_unreachable_dest(self):
        self.assertRaises(NoPathError, find_path, self.graph3, 'c', 'a')

    def test_nonexistent_dest(self):
        self.assertRaises(NoPathError, find_path, self.graph3, 'a', 'z')

    def test_all_paths(self):
        paths = single_source_shortest_paths(self.graph3, 'a')
        expected = {
            'a': (None, None, None),
            'd': ('a', 1, 1),
            'b': ('d', 1, 1),
            'e': ('d', 1, 1),
            'f': ('e', 1, 1),
            'c': ('f', 1, 1),
        }
        self.assertEqual(paths, expected)

    def test_start_and_destination_same(self):
        result = find_path(self.graph1, 1, 1)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1])
        self.assertEqual(edges, [])
        self.assertEqual(costs, [])
        self.assertEqual(total_cost, 0)
