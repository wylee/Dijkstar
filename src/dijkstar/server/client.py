import inspect
import json
from typing import Any, Callable

import requests


__all__ = ["Client", "ClientError"]


class ClientError(Exception):
    def __init__(self, response):
        super().__init__(response)
        data = response.json()
        self.response = response
        self.status_code = response.status_code
        self.explanation = data["explanation"]
        self.detail = data["detail"]

    def __str__(self):
        return f"{self.status_code}: {self.explanation}: {self.detail}"


def route(method):
    # Internal: Marks client methods as routes.
    method.is_dijkstar_client_route = True
    return method


class Client:

    """Client interface.

    For more details, see the corresponding functions in the
    :mod:`endpoints` module.

    Args:
        base_url: Server base URL.
        node_serializer:
        node_deserializer:
        edge_serializer:
        edge_deserializer:

    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        node_serializer: Callable[[Any], str] = json.dumps,
        node_deserializer: Callable[[str], Any] = json.loads,
        edge_serializer: Callable[[Any], str] = json.dumps,
        edge_deserializer: Callable[[str], Any] = json.loads,
    ):
        base_url = base_url.rstrip("/")
        self.base_url = base_url
        self.node_serializer = node_serializer
        self.node_deserializer = node_deserializer
        self.edge_serializer = edge_serializer
        self.edge_deserializer = edge_deserializer
        self.routes = self._collect_routes(base_url)

    def _collect_routes(self, base_url):
        # Find client methods decorated with @route. Collect into dict
        # of route name => route URL.
        routes = {}
        public_names = (name for name in dir(self) if not name.startswith("_"))
        for name in public_names:
            attr = getattr(self, name)
            if inspect.ismethod(attr) and getattr(
                attr, "is_dijkstar_client_route", False
            ):
                route_name = name.replace("_", "-")
                routes[route_name] = f"{base_url}/{route_name}"
        return routes

    def _route_url(self, route_name, path=None):
        route_url = self.routes[route_name]
        url = "/".join((route_url, path)) if path else route_url
        return url

    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        raise ClientError(response)

    def _get(self, route_name, path=None, params=None, **kwargs):
        """Send GET request to route."""
        url = self._route_url(route_name, path)
        response = requests.get(url, params, **kwargs)
        return self._handle_response(response)

    def _post(self, route_name, path=None, data=None, json=None, **kwargs):
        """Send GET request to route."""
        url = self._route_url(route_name, path)
        response = requests.post(url, data, json, **kwargs)
        return self._handle_response(response)

    @route
    def graph_info(self):
        """Get graph info."""
        return self._get("graph-info")

    @route
    def load_graph(self, file_name: str = None, graph_data: bytes = None):
        """Load graph from disk or data."""
        if file_name:
            headers = None
            data = {"file_name": file_name}
        elif graph_data:
            data = graph_data
            headers = {"Content-Type": "application/octet-stream"}
        else:
            headers = None
            data = None
        return self._post("load-graph", data=data, headers=headers)

    @route
    def reload_graph(self):
        """Reload graph from disk."""
        return self._post("reload-graph")

    @route
    def get_node(self, node: Any):
        """Get node."""
        data = self._get("get-node", f"{node}")
        node_deserializer = self.node_deserializer
        if node_deserializer is not None:
            data = {node_deserializer(v): edge for v, edge in data.items()}
        return data

    @route
    def get_edge(self, u: Any, v: Any):
        """Get node."""
        return self._get("get-edge", f"{u}/{v}")

    @route
    def find_path(
        self,
        start_node: Any,
        destination_node: Any,
        annex_nodes: tuple = None,
        annex_edges: tuple = None,
        cost_func: str = None,
        heuristic_func: str = None,
        fields: tuple = None,
    ):
        """Find path in graph from start node ``s`` to ``d``."""
        params = {}
        node_serializer = self.node_serializer
        edge_serializer = self.edge_serializer
        if annex_nodes:
            if node_serializer is not None:
                annex_nodes = (node_serializer(node) for node in annex_nodes)
            params["annex_nodes"] = ";".join(annex_nodes)
        if annex_edges:
            annex_edges_param = []
            for u, v, edge in annex_edges:
                if node_serializer is not None:
                    u = node_serializer(u)
                    v = node_serializer(v)
                if edge_serializer is not None:
                    edge = edge_serializer(edge)
                annex_edges_param.append(f"{u}:{v}:{edge}")
            params["annex_edges"] = ";".join(annex_edges_param)
        if cost_func:
            params["cost_func"] = cost_func
        if heuristic_func:
            params["heuristic_func"] = heuristic_func
        if fields:
            params["fields"] = ";".join(fields)
        return self._get("find-path", f"{start_node}/{destination_node}", params)

    def __str__(self):
        items = ["Dijkstar Client", f"Base URL: {self.base_url}", "Routes:"]
        items.extend(f"    {name} => {url}" for name, url in self.routes.items())
        return "\n".join(items)
