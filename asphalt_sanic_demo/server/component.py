import logging

from asphalt.core import Component
from asphalt.core.context import context_teardown

from .server import server
from .request import ContextualRequest

logger = logging.getLogger(__name__)


class ServerComponent(Component):
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port

    @context_teardown
    async def start(self, ctx):
        ContextualRequest.root_ctx = ctx
        server.ctx = ctx
        ctx.add_resource(server, context_attr='server')
        serve = server.create_server(
            host=self.host,
            port=self.port,
        )
        task = ctx.loop.create_task(serve)
        yield
        task.cancel()
