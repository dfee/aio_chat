import logging

from asphalt.core import (
    Component,
    Context,
    context_teardown,
)
from sqlalchemy.orm import Session

from ..models import Base
from .server import server

logger = logging.getLogger(__name__)


class ServerComponent(Component):
    def __init__(self, host='127.0.0.1', port=8000, debug=False, ssl=None):
        self.host = host
        self.port = port
        self.debug = debug
        self.ssl = ssl

    @context_teardown
    async def start(self, ctx):
        server.ctx = ctx
        ctx.add_resource(server, context_attr='server')

        # Set up tables
        sql = await ctx.request_resource(Session)
        async with Context(ctx) as subctx:
            Base.metadata.create_all(subctx.sql.bind)

        serve = server.create_server(
            host=self.host,
            port=self.port,
            debug=self.debug,
            ssl=self.ssl,
        )
        task = ctx.loop.create_task(serve)
        yield
        task.cancel()
