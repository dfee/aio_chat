import logging

import aioredis
from asphalt.core import (
    Component,
    context_teardown,
)

from .pubsub import PubSub

logger = logging.getLogger(__name__)


class PubSubComponent(Component):
    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 ssl=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ssl = ssl

    @context_teardown
    async def start(self, ctx):
        # TODO, when `asphalt-redis` moves away from the now deprecated
        # `aioredis.create_reconnecting_redis` to something more sane like
        # `aioredis.create_pool`, perhaps we can evict a connection from the
        # thread pool rather than creating a new connection...
        await ctx.request_resource(aioredis.Redis)

        conn = await aioredis.create_redis(
            (self.host, self.port),
            db=self.db,
            password=self.password,
            ssl=self.ssl,
        )
        pubsub = PubSub(ctx, conn)
        ctx.add_resource(pubsub, context_attr='pubsub')
        task = ctx.loop.create_task(pubsub.reader())

        yield

        conn.close()
        await conn.wait_closed()
        task.cancel()
