import io
import json

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.schemas import OpenAPIResponse, SchemaGenerator
from starlette.templating import _TemplateResponse

from .. import algorithm, Graph
from . import utils
from .templates import render_template


__all__ = [
    "get_edge",
    "get_node",
    "find_path",
    "graph_info",
    "home",
    "schema",
]


schemas = SchemaGenerator(
    {
        "openapi": "3.0.0",
        "info": {
            "title": "Dijkstar Server API",
            "version": "1.0",
        },
    }
)


class JSONOpenAPIResponse(OpenAPIResponse):

    media_type = f"{OpenAPIResponse.media_type}+json"

    def render(self, content: dict, as_json=False) -> bytes:
        return json.dumps(content).encode("utf-8")


async def schema(request: Request) -> OpenAPIResponse:
    """Render OpenAPI schema as YAML or JSON."""
    content = schemas.get_schema(request.app.routes)
    if request.url.path.endswith(".json"):
        return JSONOpenAPIResponse(content)
    return OpenAPIResponse(content)


async def home(request: Request) -> _TemplateResponse:
    """Show a list of API endpoints.

    ---
    responses:
        200:
            description: List of API endpoints

    """
    content = schemas.get_schema(request.app.routes)
    return render_template(request, "home.html", {"content": content})


async def graph_info(request: Request) -> JSONResponse:
    """Show graph info.

    ---
    responses:
        200:
            description: Graph info

    """
    graph = request.app.state.graph
    return JSONResponse(
        {
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
        }
    )


async def load_graph(request: Request) -> JSONResponse:
    """Load graph.

    This handles three cases:

        1. No graph specified: load graph file specified in settings or,
           if one wasn't specified, load a new, emtpy graph
        2. Graph file specified: load the specified graph from disk
        3. Graph data passed via POST: load that graph data

    ---
    responses:
        200:
            description: Message indicating graph was loaded

    """
    app = request.app
    settings = app.state.settings
    content_type = request.headers.get("Content-Type")

    file_name = None
    file_type = None
    graph_data = None

    if content_type == "application/x-www-form-urlencoded":
        form_data = await request.form()
        file_name = form_data.get("file_name")
        file_type = form_data.get("file_type")
    elif content_type == "application/octet-stream":
        graph_data = await request.body()

    if file_name:
        graph = Graph.guess_load(file_name, file_type)
        message = f"Graph loaded from {file_name}"
        if file_type:
            message = f"{message} ({file_type})"
    elif graph_data:
        file = io.BytesIO(graph_data)
        file.seek(0)
        graph = Graph.guess_load(file)
        message = "Graph loaded from data"
    else:
        graph = utils.load_graph(settings)
        if settings.graph_file:
            message = f"Graph reloaded from {settings.graph_file}"

    app.state.graph = graph
    return JSONResponse(message)


async def reload_graph(request: Request) -> JSONResponse:
    """Reload graph.

    If the graph was loaded from disk on startup, the graph file will be
    reloaded. Otherwise, a new graph will be loaded.

    ---
    responses:
        200:
            description: Message indicating graph was reloaded

    """
    app = request.app
    settings = app.state.settings
    app.state.graph = utils.load_graph(settings)
    if settings.graph_file:
        message = f"Graph reloaded from {settings.graph_file}"
    else:
        message = "Created a new graph since no graph file was specified"
    return JSONResponse(message)


async def get_node(request: Request) -> JSONResponse:
    """Get node.

    ---
    parameters:
        - in: path
          name: node
          required: true
    responses:
        200:
            description: The requested node
        400:
            description: The requested node doesn't exit

    """
    state = request.app.state
    graph = state.graph
    node_deserializer = state.settings.node_deserializer
    path_params = request.path_params
    node = path_params["node"]
    if node_deserializer is not None:
        node = node_deserializer(node)
    try:
        data = graph[node]
    except KeyError:
        raise HTTPException(404, f"Node {node} not found in graph")
    return JSONResponse(data)


async def get_edge(request: Request) -> JSONResponse:
    """Get edge.

    ---
    parameters:
        - in: path
          name: u
          required: true
        - in: path
          name: v
          required: true
    responses:
        200:
            description: The requested edge
        400:
            description: The requested edge doesn't exit

    """
    state = request.app.state
    graph = state.graph
    node_deserializer = state.settings.node_deserializer
    path_params = request.path_params
    u, v = path_params["u"], path_params["v"]
    if node_deserializer is not None:
        u, v = node_deserializer(u), node_deserializer(v)
    try:
        data = graph.get_edge(u, v)
    except KeyError:
        raise HTTPException(404, f"Edge ({u}, {v}) not found in graph")
    return JSONResponse(data)


async def find_path(request: Request) -> JSONResponse:
    """Find path between two nodes.

    ---
    parameters:
        - in: path
          name: start_node
          required: true
          description: Start node
        - in: path
          name: destination_node
          required: true
          description: Destination node
        - in: query
          name: annex_nodes
          required: false
          format: Semicolon-separated list of nodes
          description:
              Nodes from the main graph to copy to the annex graph.
              Direct travel between these nodes is disabled--the edges
              between them are removed from the annex graph.
        - in: query
          name: annex_edges
          required: false
          format: Semicolon-separated list of edges; each edge has the
              form "{u}:{v}:{edge_data}"
          description: Additional edges to add to the annex graph.
        - in: query
          name: cost_func
          required: false
          format: Import path like 'package.module:cost_func'
          description: Alternative cost function
        - in: query
          name: heuristic_func
          required: false
          format: Import path like 'package.module:heuristic_func'
          description: Alternative heuristic function
        - in: query
          name: fields
          required: false
          format: Semicolon-separated list of fields
          description:
              :class:`PathInfo` fields to include in response
    responses:
        200:
            description: A :class:`PathInfo` as a dict
        400:
            description:
                - Start node or end node not present in graph
                - Unknown :class:`PathInfo` field name specified
        404:
            description:
                Start or destination node doesn't exist or path not
                found

    """
    state = request.app.state
    settings = state.settings
    graph = state.graph

    node_deserializer = settings.node_deserializer
    edge_deserializer = settings.edge_deserializer

    path_params = request.path_params
    query_params = request.query_params

    start_node = path_params["start_node"]
    destination_node = path_params["destination_node"]

    if node_deserializer is not None:
        start_node = node_deserializer(start_node)
        destination_node = node_deserializer(destination_node)

    annex = None

    annex_nodes = query_params.get("annex_nodes")
    if annex_nodes:
        annex_nodes = annex_nodes.split(";")
        if node_deserializer is not None:
            annex_nodes = [node_deserializer(n) for n in annex_nodes]
        annex = graph.subgraph(annex_nodes, disconnect=True)

    annex_edges = query_params.get("annex_edges")
    if annex_edges:
        if annex is None:
            annex = Graph()
        annex_edges = annex_edges.split(";")
        for item in annex_edges:
            u, v, edge = item.split(":", 2)
            if node_deserializer is not None:
                u, v = node_deserializer(u), node_deserializer(v)
            if edge_deserializer is not None:
                edge = edge_deserializer(edge)
            annex.add_edge(u, v, edge)

    if start_node not in graph and start_node not in annex:
        raise HTTPException(400, f"Node {start_node} not present in graph")
    if destination_node not in graph and destination_node not in annex:
        raise HTTPException(400, f"Node {destination_node} not present in graph")

    cost_func = query_params.get("cost_func")
    cost_func = utils.import_object(cost_func) or settings.cost_func

    heuristic_func = query_params.get("heuristic_func")
    heuristic_func = utils.import_object(heuristic_func) or settings.heuristic_func

    fields = (query_params.get("fields") or "").strip()
    if fields:
        fields = set(name.strip() for name in fields.split(";"))

    try:
        info = algorithm.find_path(
            graph,
            start_node,
            destination_node,
            annex or None,
            cost_func,
            heuristic_func,
        )
    except algorithm.NoPathError as exc:
        raise HTTPException(404, str(exc))

    info = info._asdict()

    if fields:
        filtered_info = {}
        for name in fields:
            if name in info:
                filtered_info[name] = info[name]
            else:
                raise HTTPException(400, f"Invalid PathInfo field name: {name}")
        info = filtered_info

    return JSONResponse(info)
