import http
import logging

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import endpoints, utils
from .conf import settings


__all__ = ["app"]


# XXX: Needs to be here so our custom logging config will be loaded when
#      uvicorn auto-reloads.
utils.configure_logging(settings)


log = logging.getLogger(__name__)


# Routes


routes = (
    Route("/", endpoints.home, name="home"),
    Route("/schema", endpoints.schema, include_in_schema=False),
    Route("/schema.json", endpoints.schema, include_in_schema=False),
    Route("/graph-info", endpoints.graph_info, name="graph-info"),
    Route("/load-graph", endpoints.load_graph, methods=["POST"], name="load-graph"),
    Route(
        "/reload-graph", endpoints.reload_graph, methods=["POST"], name="reload-graph"
    ),
    Route("/get-node/{node}", endpoints.get_node, name="get-node"),
    Route("/get-edge/{u}/{v}", endpoints.get_edge, name="get-edge"),
    Route(
        "/find-path/{start_node}/{destination_node}",
        endpoints.find_path,
        name="find-path",
    ),
)


# Exception Handlers


async def handler_exception(request: Request, exc: Exception) -> JSONResponse:
    return make_error_response(500, str(exc))


async def handler_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return make_error_response(exc.status_code, exc.detail)


def make_error_response(status_code, detail) -> JSONResponse:
    return JSONResponse(
        {
            "status_code": status_code,
            "explanation": http.HTTPStatus(status_code).phrase,
            "detail": detail,
        },
        status_code=status_code,
    )


# Event Handlers


def on_startup():
    app.state.settings = settings
    app.state.graph = utils.load_graph(settings)


# App


app = Starlette(
    debug=settings.debug,
    routes=routes,
    exception_handlers={
        Exception: handler_exception,
        HTTPException: handler_http_exception,
    },
    on_startup=[on_startup],
)
