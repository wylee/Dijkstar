import unittest

from dijkstar import find_path


class Tests(unittest.TestCase):

    def setUp(self):
        self.graph = {
            'nodes': {
                1: {2: 1, 3: 3},
                2: {1: 1, 4: 6, 5: 2},
                3: {4: 4},
                4: {2: 6, 3: 4, 5: 5},
                5: {2: 2, 4: 5},
            },
            'edges': {
                1: (1,),
                2: (2,),
                3: (2,),
                4: (2,),
                5: (1,),
                6: (2,),
            }
        }
        self.annex = {'nodes': {}, 'edges': {}}

    def test(self):
        result = find_path(self.graph, self.annex, 1, 4)
        nodes, edges, costs, total_cost = result
        self.assertEqual(nodes, [1, 2, 4])
        self.assertEqual(edges, [1, 6])
        self.assertEqual(costs, [1, 2])
        self.assertEqual(total_cost, 3)
