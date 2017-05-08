import aiohttp
from aiohttp import web

from .middleware import context_middleware_factory
from .views import (
    WebSocketView,
    index,
)

async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(
            code=aiohttp.WSCloseCode.GOING_AWAY,
            message='Server shutdown',
        )

def get_app():
    app = web.Application(
        middlewares=[context_middleware_factory],
    )
    app.router.add_get('/', index)
    app.router.add_route('*', '/ws', WebSocketView)
    app['websockets'] = []
    app.on_shutdown.append(on_shutdown)
    return app
