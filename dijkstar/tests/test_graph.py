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
        if os.path.exists(cls.pickle_file):
            os.remove(cls.pickle_file)
        if os.path.exists(cls.marshal_file):
            os.remove(cls.marshal_file)

    def _check_graph(self, graph):
        self.assertEqual(graph, self.graph)
        self.assertEqual(graph._incoming, self.graph._incoming)

    def test_subgraph(self):
        subgraph = self.graph.subgraph((1, 2))
        self.assertEqual(sorted(subgraph), [1, 2])
        self.assertEqual(subgraph[1], self.graph[1])
        self.assertEqual(subgraph[2], self.graph[2])

    def test_subgraph_with_disconnect(self):
        subgraph = self.graph.subgraph((1, 2), disconnect=True)
        self.assertEqual(sorted(subgraph), [1, 2])
        self.assertEqual(subgraph[1], {4: 1})
        self.assertEqual(subgraph[2], {3: 1, 5: 1})

    def test_1_dump(self):
        self.graph.dump(self.pickle_file)
        self.assertTrue(os.path.exists(self.pickle_file))

    def test_2_load(self):
        graph = Graph.load(self.pickle_file)
        self._check_graph(graph)

    def test_3_dump_to_open_file(self):
        with open(self.pickle_file, 'wb') as fp:
            self.graph.dump(fp)

    def test_4_load_from_open_file(self):
        with open(self.pickle_file, 'rb') as fp:
            graph = self.graph.load(fp)
        self._check_graph(graph)

    def test_1_marshal(self):
        self.graph.marshal(self.marshal_file)
        self.assertTrue(os.path.exists(self.marshal_file))

    def test_2_unmarshal(self):
        graph = Graph.unmarshal(self.marshal_file)
        self._check_graph(graph)


class TestUndirectedGraph(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create by adding edges
        graph1 = Graph(undirected=True)
        graph1.add_edge(1, 2)
        graph1.add_edge(1, 3)
        graph1.add_edge(2, 4)
        graph1.add_edge(3, 4)
        cls.graph1 = graph1

        # Create by adding nodes with neighbors
        graph2 = Graph(undirected=True)
        graph2.add_node(1, {2: None, 3: None})
        graph2.add_node(2, {4: None})
        graph2.add_node(3, {4: None})
        cls.graph2 = graph2

        # Create with initial data (nodes & neighbors)
        graph3 = Graph({
            1: {2: None, 3: None},
            2: {4: None},
            3: {4: None},
        }, undirected=True)
        cls.graph3 = graph3

    def test_edge_count(self):
        self.assertEqual(self.graph1.edge_count, 4)
        self.assertEqual(self.graph2.edge_count, 4)
        self.assertEqual(self.graph3.edge_count, 4)

    def test_node_count(self):
        self.assertEqual(self.graph1.node_count, 4)
        self.assertEqual(self.graph2.node_count, 4)
        self.assertEqual(self.graph3.node_count, 4)

    def test_add_edge_vs_add_node(self):
        self.assertEqual(self.graph1, self.graph3)

    def test_add_edge_vs_initial_data(self):
        self.assertEqual(self.graph1, self.graph3)

    def test_delete_node(self):
        graph = Graph(undirected=True)
        graph.add_edge(1, 2)
        graph.add_edge(1, 3)
        graph.add_edge(2, 4)
        graph.add_edge(3, 4)
        self.assertEqual(graph.edge_count, 4)
        self.assertEqual(graph.node_count, 4)
        self.assertEqual(graph, {
            1: {2: None, 3: None},
            2: {1: None, 4: None},
            3: {1: None, 4: None},
            4: {2: None, 3: None},
        })
        self.assertEqual(graph._incoming, {
            1: {2: None, 3: None},
            2: {1: None, 4: None},
            3: {1: None, 4: None},
            4: {2: None, 3: None},
        })
        del graph[1]
        self.assertEqual(graph.edge_count, 2)
        self.assertEqual(graph.node_count, 3)
        self.assertEqual(graph, {
            2: {4: None},
            3: {4: None},
            4: {2: None, 3: None},
        })
        self.assertEqual(graph._incoming, {
            2: {4: None},
            3: {4: None},
            4: {2: None, 3: None},
        })
        del graph[4]
        self.assertEqual(graph.edge_count, 0)
        self.assertEqual(graph.node_count, 2)
        self.assertEqual(graph, {
            2: {},
            3: {},
        })
        self.assertEqual(graph._incoming, {})
