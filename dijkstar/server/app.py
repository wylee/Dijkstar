import http
import logging

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import endpoints, utils
from .conf import settings


__all__ = ['app']


# XXX: Needs to be here so our custom logging config will be loaded when
#      uvicorn auto-reloads.
utils.configure_logging(settings)


log = logging.getLogger(__name__)

app = Starlette(debug=settings.debug)


# Routes


app.add_route('/', endpoints.home)
app.add_route('/schema', endpoints.schema, include_in_schema=False)
app.add_route('/schema.json', endpoints.schema, include_in_schema=False)
app.add_route('/graph-info', endpoints.graph_info)
app.add_route('/load-graph', endpoints.load_graph, methods=['POST'])
app.add_route('/reload-graph', endpoints.reload_graph, methods=['POST'])
app.add_route('/get-node/{node}', endpoints.get_node)
app.add_route('/get-edge/{u}/{v}', endpoints.get_edge)
app.add_route('/find-path/{start_node}/{destination_node}', endpoints.find_path)


# Exception Handlers


def make_error_response(status_code, detail) -> JSONResponse:
    return JSONResponse({
        'status_code': status_code,
        'explanation': http.HTTPStatus(status_code).phrase,
        'detail': detail,
    }, status_code=status_code)


async def handler_exception(request: Request, exc: Exception) -> JSONResponse:
    return make_error_response(500, str(exc))


async def handler_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return make_error_response(exc.status_code, exc.detail)


app.add_exception_handler(Exception, handler_exception)
app.add_exception_handler(HTTPException, handler_http_exception)


# Event Handlers


def handler_startup():
    app.state.settings = settings
    app.state.graph = utils.load_graph(settings)


app.add_event_handler('startup', handler_startup)
