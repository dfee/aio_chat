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
        # TODO, upon 1.0 release of `aioredis` and an update to `asphalt-redis`
        # where `aioredis.create_reconnecting_redis` is moved to something more
        # sane like `aioredis.create_pool`, migrate away from `aio_chat.redis`
        # back to regular `asphalt-redis`

        pool = await ctx.request_resource(aioredis.RedisPool)
        conn = await pool.acquire()
        pubsub = PubSub(ctx, conn, pool)
        ctx.add_resource(pubsub, context_attr='pubsub')
        task = ctx.loop.create_task(pubsub.reader())

        yield

        task.cancel()
        pool.release(conn)
        pool.close()
        await pool.wait_closed()
