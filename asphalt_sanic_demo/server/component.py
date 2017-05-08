import logging

from asphalt.core import (
    Component,
    Context,
    context_teardown,
)
from sqlalchemy.orm import Session

from ..models import Base
from .app import get_app

logger = logging.getLogger(__name__)


class ServerComponent(Component):
    def __init__(self, host='127.0.0.1', port=8000, debug=False, ssl=None):
        self.host = host
        self.port = port
        self.debug = debug
        self.ssl = ssl

    @context_teardown
    async def start(self, ctx):
        # Require PubSub so we shut down before PubSub does.
        from ..pubsub import PubSub
        await ctx.request_resource(PubSub)

        # Set up tables
        sql = await ctx.request_resource(Session)
        async with Context(ctx) as subctx:
            Base.metadata.create_all(subctx.sql.bind)

        # Set up app
        app = get_app()
        app.ctx = ctx

        handler = app.make_handler()
        server = await ctx.loop.create_server(handler, self.host, self.port)
        logger.info('Serving on {}:{}'.format(self.host, self.port))

        yield

        server.close()
        await server.wait_closed()
        await app.shutdown()
        await handler.shutdown(5.0)
        await app.cleanup()
