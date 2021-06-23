import inspect
import io
import multiprocessing
import os
import socket
import sys
import tempfile
import time
import unittest

import requests
import uvicorn

from dijkstar.graph import Graph
from dijkstar.server import utils
from dijkstar.server.client import Client
from dijkstar.server.conf import settings


class TestUtils(unittest.TestCase):
    def test_import_object(self):
        obj = utils.import_object("tests.test_server:TestUtils")
        self.assertIs(obj, self.__class__)

    def test_import_object_none(self):
        obj = utils.import_object(None)
        self.assertIsNone(obj)

    def test_load_graph(self):
        with tempfile.NamedTemporaryFile(suffix=".marshal") as file:
            graph = Graph()
            graph.add_edge(1, 2)
            graph.marshal(file)
            file.flush()
            with utils.modified_settings(graph_file=file.name):
                loaded_graph = utils.load_graph(settings)
        self.assertEqual(loaded_graph, graph)

    def test_load_no_graph(self):
        graph = utils.load_graph(settings)
        self.assertEqual(graph, Graph())

    def test_modified_settings(self):
        self.assertIsNone(settings.graph_file)
        with utils.modified_settings(graph_file="test_graph_file.marshal"):
            self.assertEqual(settings.graph_file, "test_graph_file.marshal")
        self.assertIsNone(settings.graph_file)


class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def get_free_port():
            sock = socket.socket()
            sock.bind(("", 0))
            port = sock.getsockname()[1]
            sock.close()
            return port

        # 1 - - - → 2
        # |         |
        # |         |
        # ↓         ↓
        # 3 - - - → 4
        graph_file = tempfile.NamedTemporaryFile(delete=False, suffix=".marshal")
        graph = Graph()
        graph.add_edge(1, 2, 1)
        graph.add_edge(1, 3, 1)
        graph.add_edge(2, 4, 1)
        graph.add_edge(3, 4, 1)
        graph.marshal(graph_file)
        graph_file.flush()
        graph_file.close()

        cls.host = "127.0.0.1"
        cls.port = get_free_port()
        cls.base_url = f"http://{cls.host}:{cls.port}"
        cls.graph = graph
        cls.graph_file = graph_file.name

        cls.server_process = multiprocessing.Process(
            target=uvicorn.run,
            args=("dijkstar.server.app:app",),
            kwargs={
                "host": cls.host,
                "port": cls.port,
                "log_level": "error",
            },
        )

        # XXX: This has to be set for Python 3.8 only (???)
        os.environ["GRAPH_FILE"] = graph_file.name

        with utils.modified_settings(graph_file=cls.graph_file):
            cls.server_process.start()

        attempts_left = 20
        sleep_time = 0.1
        total_seconds = int(round(attempts_left * sleep_time))
        while attempts_left > 0:
            try:
                requests.get(cls.base_url)
            except requests.ConnectionError:
                attempts_left -= 1
                if attempts_left > 0:
                    time.sleep(sleep_time)
                else:
                    print(
                        f"WARNING: Failed to connect to server after {total_seconds} seconds",
                        file=sys.stderr,
                    )
                    for name in dir(cls):
                        if name.startswith("test_"):
                            attr = getattr(cls, name)
                            if inspect.isfunction(attr):
                                decorated = unittest.skip(
                                    "Could not connect to client"
                                )(attr)
                                setattr(cls, name, decorated)
            else:
                break

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.join()
        os.remove(cls.graph_file)

    def setUp(self):
        self.client = self.make_client()

    def make_client(self, base_url=None):
        return Client(base_url or self.base_url)

    def test_routes(self):
        client = self.client
        self.assertEqual(len(client.routes), 6)
        self.assertIn("graph-info", client.routes)
        self.assertIn("get-node", client.routes)
        self.assertIn("get-edge", client.routes)
        self.assertIn("find-path", client.routes)

    def test_get_graph_info(self):
        client = self.client
        data = client.graph_info()
        self.assertIn("edge_count", data)
        self.assertIn("node_count", data)
        self.assertEqual(data["edge_count"], 4)
        self.assertEqual(data["node_count"], 4)

    def test_load_graph(self):
        client = self.client
        message = client.load_graph()
        self.assertEqual(message, f"Graph reloaded from {self.graph_file}")

    def test_load_graph_from_file(self):
        client = self.client
        message = client.load_graph(file_name=self.graph_file)
        self.assertEqual(message, f"Graph loaded from {self.graph_file}")

    def test_load_graph_from_data(self):
        client = self.client
        file = io.BytesIO()
        self.graph.marshal(file)
        file.seek(0)
        message = client.load_graph(graph_data=file.getvalue())
        self.assertEqual(message, "Graph loaded from data")

    def test_reload_graph(self):
        client = self.client
        message = client.reload_graph()
        self.assertEqual(message, f"Graph reloaded from {self.graph_file}")

    def test_get_node(self):
        client = self.client
        data = client.get_node(1)
        self.assertEqual(data, self.graph[1])

    def test_get_edge(self):
        client = self.client
        data = client.get_edge(1, 2)
        self.assertEqual(data, self.graph.get_edge(1, 2))

    def test_find_path(self):
        client = self.client
        data = client.find_path(1, 4)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIn("costs", data)
        self.assertIn("total_cost", data)
        nodes = data["nodes"]
        edges = data["edges"]
        self.assertEqual(len(nodes), 3)
        self.assertEqual(len(edges), 2)
        self.assertEqual(nodes, [1, 2, 4])
        self.assertEqual(edges, [1, 1])

    def test_find_path_with_annex(self):
        client = self.client
        # Insert node between nodes 1 and 2 then find a path from that
        # node (-1) to node 4.
        data = client.find_path(
            -1,
            4,
            annex_nodes=(1, 2),
            annex_edges=(
                (1, -1, 1.1),
                (-1, 2, 1.2),
            ),
        )
        nodes = data["nodes"]
        edges = data["edges"]
        self.assertEqual(len(nodes), 3)
        self.assertEqual(len(edges), 2)
        self.assertEqual(nodes, [-1, 2, 4])
        self.assertEqual(edges, [1.2, 1])
