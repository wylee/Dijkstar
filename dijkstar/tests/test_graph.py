import os
import tempfile
import unittest


from dijkstar.graph import Graph


class TestGraph(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pickle_file = tempfile.mktemp()
        cls.marshal_file = tempfile.mktemp()
        cls.graph = Graph({
            1: {2: 1, 4: 1},
            2: {1: 1, 3: 1, 5: 1},
            3: {2: 1, 6: 1},
            4: {1: 1, 5: 1, 7: 1},
            5: {2: 1, 4: 1, 6: 1, 8: 1},
            6: {3: 1, 5: 1, 9: 1},
            7: {4: 1, 8: 1},
            8: {5: 1, 7: 1, 9: 1},
            9: {6: 1, 8: 1},
        })

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.pickle_file)
        os.remove(cls.marshal_file)

    def test_1_dump(self):
        self.graph.dump(self.pickle_file)
        self.assertTrue(os.path.exists(self.pickle_file))

    def test_2_load(self):
        graph = Graph.load(self.pickle_file)
        self.assertEqual(graph, self.graph)
        self.assertEqual(graph._data, self.graph._data)
        self.assertEqual(graph._incoming, self.graph._incoming)

    def test_1_marshal(self):
        self.graph.marshal(self.marshal_file)
        self.assertTrue(os.path.exists(self.marshal_file))

    def test_2_unmarshal(self):
        graph = Graph.unmarshal(self.marshal_file)
        self.assertEqual(graph, self.graph)
        self.assertEqual(graph._data, self.graph._data)
        self.assertEqual(graph._incoming, self.graph._incoming)
