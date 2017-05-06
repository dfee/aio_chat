import asyncio
import json

import aioredis
from aioredis.pubsub import Receiver
from aioredis.abc import AbcChannel
from asphalt.core import (
    Component,
    context_teardown,
)


# TODO: Swap out for normal implementation once this is fixed:
# https://github.com/aio-libs/aioredis/issues/203
# http://aioredis.readthedocs.io/en/v0.3.0/mpsc.html#aioredis.pubsub.Receiver
class IterableReceiver(Receiver):
    def __aiter__(self):
        return self

    async def __anext__(self):
        loop = asyncio.get_event_loop()
        await self.wait_message()
        return await self.get()


class PubSub:
    def __init__(self, ctx, subscribe_conn, publish_conn):
        self.ctx = ctx
        self.subscribe_conn = subscribe_conn
        self.publish_conn = publish_conn
        self.queue = asyncio.Queue()
        self.mpsc = IterableReceiver(loop=ctx.loop)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.queue.get()

    def encode(self, string, encoding='utf-8', errors='strict'):
        if isinstance(string, bytes):
            return string
        return string.encode(encoding, errors)

    async def run(self):
        async for channel, message in self.mpsc:
            assert isinstance(channel, AbcChannel)
            print(channel.name, message)
            await self.queue.put((channel.name, message))

    async def publish(self, channel_id, message):
        # TODO, perhaps publisher_conn should be ephemeral / attached to the
        # context of the caller? Likely oughta be event driven.
        e_channel_id = self.encode(channel_id)
        e_message = self.encode(message)
        await self.publish_conn.publish(e_channel_id, e_message)

    async def subscribe(self, channel_id):
        e_channel_id = self.encode(channel_id)
        channel = self.mpsc.channel(e_channel_id)
        await self.subscribe_conn.subscribe(channel)

    async def unsubscribe(self, channel_id):
        e_channel_id = self.encode(channel_id)
        channel = self.mpsc.channels.get(e_channel_id)
        if channel:
            await self.subscribe_conn.unsubscribe(channel)

    async def teardown(self):
        for channel_id in self.mpsc.channels:
            await self.subscribe_conn.unsubscribe(channel_id)


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
        # TODO, figure out how to evict a conn from the redis-pool?
        subscribe_conn = await aioredis.create_redis(
            (self.host, self.port),
            db=self.db,
            password=self.password,
            ssl=self.ssl,
        )
        mpsc = IterableReceiver(loop=ctx.loop)
        redis = await ctx.request_resource(aioredis.Redis)
        pubsub = PubSub(ctx, subscribe_conn, redis)
        ctx.add_resource(pubsub, context_attr='pubsub')
        task = ctx.loop.create_task(pubsub.run())

        yield

        task.cancel()
        await pubsub.teardown()
        subscribe_conn.close()
        await subscribe_conn.wait_closed()
