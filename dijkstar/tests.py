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
            'b': {'a': 1, 'c': 1, 'e': 1},
            'c': {'b': 1, 'f': 1},
            'd': {'a': 1, 'e': 1, 'g': 1},
            'e': {'b': 1, 'd': 1, 'f': 1, 'h': 1},
            'f': {'c': 1, 'e': 1, 'i': 1},
            'g': {'d': 1, 'h': 1},
            'h': {'e': 1, 'g': 1, 'i': 1},
            'i': {'f': 1, 'h': 1}
        })

        self.graph3 = Graph({
            'a': {'b': 10, 'c': 100, 'd': 1},
            'b': {'c': 10},
            'd': {'b': 1, 'e': 1},
            'e': {'f': 1},
            'f': {'c': 1},
            'g': {'b': 1}
        })

    def test_find_path_1(self):
        result = find_path(self.graph1, 1, 4)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1, 2, 4])
        self.assertEqual(edges, [1, 2])
        self.assertEqual(costs, [1, 2])
        self.assertEqual(total_cost, 3)

    def test_find_path_2(self):
        path = find_path(self.graph2, 'a', 'i')[0];
        self.assertEqual(path, ['a', 'd', 'e', 'f', 'i']);

    def test_find_path_3(self):
        path = find_path(self.graph3, 'a', 'c')[0];
        self.assertEqual(path, ['a', 'd', 'e', 'f', 'c']);

    def test_unreachable_dest(self):
        self.assertRaises(NoPathError, find_path, self.graph3, 'c', 'a')

    def test_nonexistent_dest(self):
        self.assertRaises(NoPathError, find_path, self.graph3, 'a', 'z')

    def test_all_paths(self):
        paths = single_source_shortest_paths(self.graph3, 'a');
        expected = {
            'a': None,
            'd': ('a', 1, 1),
            'b': ('d', 1, 1),
            'c': ('b', 1, 1),
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
