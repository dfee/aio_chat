import logging

from aioredis import Redis
from asphalt.core import  (
    Component,
    Context,
    context_teardown,
)
from asphalt.templating.api import TemplateRenderer
from sqlalchemy.orm import Session

from ..pubsub import PubSub
from .app import get_app

logger = logging.getLogger(__name__)


class ServerComponent(Component):
    def __init__(self, host='0.0.0.0', port=8000, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

    @context_teardown
    async def start(self, ctx):
        # Require relied upon resources
        #  await ctx.request_resource(Redis)
        await ctx.request_resource(PubSub)
        await ctx.request_resource(Session)
        await ctx.request_resource(TemplateRenderer)

        app = get_app()
        app.ctx = ctx
        ctx.add_resource(app, context_attr='server')
        handler = app.make_handler()
        server = await ctx.loop.create_server(handler, self.host, self.port)
        logger.info('Serving on {}:{}'.format(self.host, self.port))

        yield

        server.close()
        await server.wait_closed()
        await app.shutdown()
        await handler.shutdown(60.0)
        await app.cleanup()
