from aiohttp import web

from .middleware import context_middleware_factory
from .views import (
    WebSocketView,
    index,
)

def get_app():
    app = web.Application(
        middlewares=[context_middleware_factory],
    )
    app.router.add_get('/', index)
    app.router.add_route('*', '/ws', WebSocketView)
    return app
