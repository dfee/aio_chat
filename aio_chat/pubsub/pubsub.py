import asyncio
from enum import Enum
from functools import partial
import inspect
import logging
import pickle

from aioredis.pubsub import Receiver
from aioredis.abc import AbcChannel
from asphalt.core import Context

logger = logging.getLogger(__name__)


class RegistrationType(Enum):
    channel = 'channel'
    pattern = 'pattern'


class PubSubMessage:
    def __init__(self, channel, pattern, message):
        self.channel = channel
        self.pattern = pattern
        self.message = message

    @property
    def json(self):
        if not hasattr(self, '_json'):
            self._json = json.loads(message)
        return self._json


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
    def __init__(self, ctx, conn, pool):
        self.ctx = ctx
        self.conn = conn
        self.pool = pool
        self.mpsc = IterableReceiver(loop=ctx.loop)
        self.registry = {}

    async def reader(self):
        async for channel_or_pattern, produced in self.mpsc:
            assert isinstance(channel_or_pattern, AbcChannel)

            channel = None
            pattern = None
            message = None

            if channel_or_pattern.is_pattern:
                channel = produced[0].decode()
                message = pickle.loads(produced[1])
                pattern = channel_or_pattern.name.decode()
            else:
                channel = channel_or_pattern.name.decode()
                message = pickle.loads(produced)

            handlers = []
            if pattern:
                registration = (RegistrationType.pattern, pattern)
                handlers += self.registry.get(registration, [])
            registration = (RegistrationType.channel, channel)
            handlers += self.registry.get(registration, [])

            logger.info('Heard on channel {}: {}'.format(channel, message))

            psm = PubSubMessage(channel, pattern, message)
            for handler in handlers:
                asyncio.ensure_future(handler(psm))

    async def publish(self, channel, message):
        async with self.pool.get() as conn:
            await conn.publish(channel.encode(), pickle.dumps(message))
            logger.info('Sent messsage on {}: {}'.format(channel, message))
        #  async with Context(self.ctx) as subctx:
        #      await subctx.redis.publish(channel.encode(), pickle.dumps(message))
        #      logger.info('Sent messsage on {}: {}'.format(channel, message))

    async def subscribe(self, channel, handler):
        func = handler.func if isinstance(handler, partial) else handler
        assert inspect.iscoroutinefunction(func), \
            'Handler must be either a coroutine function or a ' \
            'partial of a coroutine function.'

        registration = (RegistrationType.channel, channel)
        if registration not in self.registry:
            mpsc_channel = self.mpsc.channel(channel)
            await self.conn.subscribe(mpsc_channel)
            logger.info('Subscribed to channel: {}'.format(channel))
            self.registry[registration] = set()
        self.registry[registration].add(handler)
        return partial(self.unsubscribe, channel, handler)

    async def psubscribe(self, pattern, handler):
        func = handler.func if isinstance(handler, partial) else handler
        assert inspect.iscoroutinefunction(func), \
            'Handler must be either a coroutine function or a ' \
            'partial of a coroutine function.'

        registration = (RegistrationType.pattern, pattern)
        if registration not in self.registry:
            mpsc_pattern = self.mpsc.pattern(pattern)
            await self.conn.psubscribe(mpsc_pattern)
            logger.info('Subscribed to pattern: {}'.format(pattern))
            self.registry[registration] = set()
        self.registry[registration].add(handler)
        return partial(self.punsubscribe, pattern, handler)

    async def unsubscribe(self, channel, handler):
        registration = (RegistrationType.channel, channel)
        if registration not in self.registry:
            return

        self.registry[registration].discard(handler)

        if not self.registry[registration]:
            del self.registry[registration]
            await self.conn.unsubscribe(channel)
            logger.info('Unsubscribed from pattern: {}'.format(channel))

    async def punsubscribe(self, pattern, handler):
        registration = (RegistrationType.pattern, pattern)
        if registration not in self.registry:
            return

        self.registry[registration].discard(handler)

        if not self.registry[registration]:
            del self.registry[registration]
            await self.conn.punsubscribe(pattern)
            logger.info('Unsubscribed from pattern: {}'.format(pattern))
