import logging

from asphalt.core import Component
from asphalt.core.context import context_teardown
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
        Base.metadata.bind = sql.connection().engine # TODO move to config?
        Base.metadata.create_all()

        serve = server.create_server(
            host=self.host,
            port=self.port,
            debug=self.debug,
            ssl=self.ssl,
        )
        task = ctx.loop.create_task(serve)
        yield
        task.cancel()
