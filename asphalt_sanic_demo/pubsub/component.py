import asyncio
import logging
import json

import aioredis
from aioredis.pubsub import Receiver
from aioredis.abc import AbcChannel
from asphalt.core import (
    Component,
    Context,
    Event,
    Signal,
    context_teardown,
)
from async_generator import aclosing

logger = logging.getLogger(__name__)


class SubscribeEvent(Event):
    def __init__(self, source, topic, channel_id):
        super().__init__(source, topic)
        self.channel_id = channel_id


class UnsubscribeEvent(Event):
    def __init__(self, source, topic, channel_id):
        super().__init__(source, topic)
        self.channel_id = channel_id


class MessageReceiveEvent(Event):
    def __init__(self, source, topic, channel_id, message):
        super().__init__(source, topic)
        self.channel_id = channel_id
        self.message = message


class MessageSendEvent(Event):
    def __init__(self, source, topic, channel_id, message):
        super().__init__(source, topic)
        self.channel_id = channel_id
        self.message = message


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
    subscribe = Signal(SubscribeEvent)
    unsubscribe = Signal(UnsubscribeEvent)
    message_received = Signal(MessageReceiveEvent)
    message_send = Signal(MessageSendEvent)

    def __init__(self, ctx, conn):
        self.ctx = ctx
        self.conn = conn
        self.queue = asyncio.Queue()
        self.mpsc = IterableReceiver(loop=ctx.loop)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.queue.get()

    async def reader(self):
        async for channel, message in self.mpsc:
            assert isinstance(channel, AbcChannel)
            print(channel.name, message)
            self.message_received.dispatch(
                channel.name.decode(),
                message.decode(),
            )
            logger.info('Received messsage on {}: {}'.format(
                channel.name.decode(),
                message.decode(),
            ))

    async def writer(self):
        # TODO: figure out why we're getting this error after sending a msg
        # and then quitting
        #  ERROR 2017-05-05 18:18:16,146 [asyncio:1259][Dummy-16] Task was destroyed but it is pending!
        #  task: <Task pending coro=<RedisConnection._read_data() running at /Users/dfee/code/asphalt_sanic_demo/env/lib/python3.6/site-packages/aioredis/connection.py:132> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x109e8caf8>()]> cb=[Future.set_result()]>
        async with aclosing(self.message_send.stream_events()) as stream:
            async for event in stream:
                async with Context(self.ctx) as subctx:
                    await subctx.redis.publish(
                        event.channel_id.encode(),
                        event.message.encode(),
                    )
                    logger.info('Sent messsage on {}: {}'.format(
                        event.channel_id,
                        event.message,
                    ))

    async def subscriber(self):
        async with aclosing(self.subscribe.stream_events()) as stream:
            async for event in stream:
                channel = self.mpsc.channel(event.channel_id.encode())
                await self.conn.subscribe(channel)
                logger.info('Subscribed to channel {}'.format(
                    event.channel_id,
                ))

    async def unsubscriber(self):
        async with aclosing(self.unsubscribe.stream_events()) as stream:
            async for event in stream:
                channel = self.mpsc.channels.get(event.channel_id.encode())
                if channel:
                    await self.conn.unsubscribe(channel)
                    logger.info('Unsubscribed from channel {}'.format(
                        event.channel_id,
                    ))

    async def teardown(self):
        for channel_id in self.mpsc.channels:
            await self.conn.unsubscribe(channel_id)


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
        conn = await aioredis.create_redis(
            (self.host, self.port),
            db=self.db,
            password=self.password,
            ssl=self.ssl,
        )
        pubsub = PubSub(ctx, conn)
        ctx.add_resource(pubsub, context_attr='pubsub')

        # TODO: is this conceptionally correct in the asphalt framework?
        # Fail early if `redis` is not a resource on the context.
        await ctx.request_resource(aioredis.Redis)

        tasks = {
            'subscriber': ctx.loop.create_task(pubsub.subscriber()),
            'unsubscriber': ctx.loop.create_task(pubsub.unsubscriber()),
            'reader': ctx.loop.create_task(pubsub.reader()),
            'writer': ctx.loop.create_task(pubsub.writer()),
        }

        yield

        for task in tasks.values():
            task.cancel()

        await pubsub.teardown()
        conn.close()
        await conn.wait_closed()
