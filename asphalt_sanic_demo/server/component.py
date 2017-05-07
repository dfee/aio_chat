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
        # Set up tables
        sql = await ctx.request_resource(Session)
        async with Context(ctx) as subctx:
            Base.metadata.create_all(subctx.sql.bind)

        # Set up app
        app = get_app()
        app.ctx = ctx

        handler = app.make_handler()
        f = await ctx.loop.create_server(handler, self.host, self.port)
        srv = ctx.loop.create_task(f)
        logger.info('Serving on {}:{}'.format(self.host, self.port))

        yield

        srv.cancel()
        await app.shutdown()
        await handler.shutdown(2.0)
        await app.cleanup()
        f.close()
        await f.wait_closed()
