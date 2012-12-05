import unittest

from dijkstar import find_path
from dijkstar.graph import Graph


class Tests(unittest.TestCase):

    def setUp(self):
        self.graph = Graph({
            1: {2: 1, 3: 2},
            2: {1: 1, 4: 2, 5: 2},
            3: {4: 2},
            4: {2: 2, 3: 2, 5: 1},
            5: {2: 2, 4: 1},
        })
        self.annex = Graph()

    def test(self):
        result = find_path(self.graph, self.annex, 1, 4)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1, 2, 4])
        self.assertEqual(edges, [1, 2])
        self.assertEqual(costs, [1, 2])
        self.assertEqual(total_cost, 3)
