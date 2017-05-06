import asyncio
from functools import partial
import inspect
import logging

from aioredis.pubsub import Receiver
from aioredis.abc import AbcChannel
from asphalt.core import Context

logger = logging.getLogger(__name__)


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
    def __init__(self, ctx, conn):
        self.ctx = ctx
        self.conn = conn
        self.mpsc = IterableReceiver(loop=ctx.loop)
        self.subscription_handlers = {}
        self.psubscription_handlers = {}

    async def reader(self):
        async for channel, _message in self.mpsc:
            assert isinstance(channel, AbcChannel)
            channel_id = channel.name.decode()
            message = _message.decode()
            logger.info('Heard on channel {}: {}'.format(channel_id, message))

            handlers = self.subscription_handlers.get(channel_id, [])
            for handler in handlers:
                asyncio.ensure_future(handler(message))

    async def publish(self, channel_id, message):
        # TODO: figure out why we're getting this error after sending a msg
        # and then quitting
        #  ERROR 2017-05-06 01:37:59,745 [asyncio:1259][Dummy-183] Task was destroyed but it is pending!
        #  task: <Task pending coro=<RedisConnection._read_data() running at /Users/dfee/code/asphalt_sanic_demo/env/lib/python3.6/site-packages/aioredis/connection.py:132> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x10b6b1168>()]> cb=[Future.set_result()]>
        async with Context(self.ctx) as subctx:
            await subctx.redis.publish(channel_id.encode(), message.encode())
            logger.info('Sent messsage on {}: {}'.format(channel_id, message))

    async def subscribe(self, channel_id, handler):
        assertion_msg = \
            'Handler must be either a coroutine function or a ' \
            'partial of a coroutine function.'
        if isinstance(handler, partial):
            assert inspect.iscoroutinefunction(handler.func), assertion_msg
        else:
            assert inspect.iscoroutinefunction(handler), assertion_msg

        if channel_id not in self.subscription_handlers:
            channel = self.mpsc.channel(channel_id.encode())
            await self.conn.subscribe(channel)
            logger.info('Subscribed to channel: {}'.format(channel_id))
            self.subscription_handlers[channel_id] = set()
        self.subscription_handlers[channel_id].add(handler)
        return partial(self.unsubscribe, channel_id, handler)

    async def psubscribe(self, channel_ptn, handler):
        assertion_msg = \
            'Handler must be either a coroutine function or a ' \
            'partial of a coroutine function.'
        if isinstance(handler, partial):
            assert inspect.iscoroutinefunction(handler.func), assertion_msg
        else:
            assert inspect.iscoroutinefunction(handler), assertion_msg

        if channel_ptn not in self.psubscription_handlers:
            channel = self.mpsc.channel(channel_ptn.encode())
            await self.conn.subscribe(channel)
            logger.info('Subscribed to pattern: {}'.format(channel_ptn))
            self.psubscription_handlers[channel_ptn] = set()
        self.psubscription_handlers[channel_ptn].add(handler)
        return partial(self.punsubscribe, channel_ptn, handler)

    async def unsubscribe(self, channel_id, handler):
        if channel_id not in self.subscription_handlers:
            return

        self.subscription_handlers[channel_id].discard(handler)

        if not self.subscription_handlers[channel_id]:
            del self.subscription_handlers[channel_id]
            channel = self.mpsc.channels.get(channel_id.encode())
            if channel:
                await self.conn.unsubscribe(channel)
                logger.info('Unsubscribed from pattern: {}'.format(channel_id))

    async def punsubscribe(self, channel_ptn, handler):
        if channel_ptn not in self.psubscription_handlers:
            return

        self.psubscription_handlers[channel_ptn].discard(handler)

        if not self.psubscription_handlers[channel_ptn]:
            del self.psubscription_handlers[channel_ptn]
            channel = self.mpsc.channels.get(channel_ptn.encode())
            if channel:
                await self.conn.unsubscribe(channel)
                logger.info('Unsubscribed from channel: {}'.format(channel_ptn))
