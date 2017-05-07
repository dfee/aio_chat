import logging
import json

from asphalt.core import (
    Context,
    executor,
)
from sanic import Sanic
from sanic.response import html

from ..models import Message
from ..pubsub import PubSubMessage
from .utils import contextualize

logger = logging.getLogger(__name__)
server = Sanic()

@executor
def render_template(ctx, messages):
    '''
    Jinja2 reads from disk, thus blocking I/O.
    There is a configuraiton setting for Jinja2 to use an async mode,
    but asphalt-templating doesn't yet support it.
    '''
    return ctx.jinja2.render('index.html', messages=messages)

@executor
def get_messages(ctx):
    '''SQLAlchemy reads from disk, thus blocking I/O.'''
    messages = ctx.sql.query(Message).all()
    # Important: when your models become more complex, you don't want to
    # issue further queries to load relationship data outside the executor.
    ctx.sql.expunge_all()
    return messages

@executor
def add_message(ctx, text):
    '''SQLAlchemy reads from disk, thus blocking I/O.'''
    message = Message(text=text)
    ctx.sql.add(message)

@server.route('/', methods=['GET'])
@contextualize
async def get_index(ctx):
    async with Context(ctx) as subctx:
        messages = await get_messages(subctx)
    rendered = await render_template(ctx, messages)
    return html(rendered)


class WebSocketSession:
    def __init__(self, ctx, ws):
        self.ctx = ctx
        self.ws = ws

    async def send(self, message):
        logger.info('Sending message: {}'.format(message))
        await self.ws.send(json.dumps(message))

    async def receive(self):
        message = await self.ws.recv()
        parsed = json.loads(message)
        logger.info('Received message: {}'.format(parsed))
        return parsed

    async def forward_psm(self, psm):
        assert isinstance(psm, PubSubMessage)
        message = {'text': psm.message.text}
        await self.send(message)

    async def __call__(self):
        unsub = await self.ctx.pubsub.psubscribe('message:*', self.forward_psm)
        try:
            while True:
                message = await self.receive()
                async with Context(self.ctx) as subctx:
                    await add_message(subctx, message['text'])
        finally:
            await unsub()


@server.websocket('/ws')
@contextualize
async def ws(ctx, ws):
    session = WebSocketSession(ctx, ws)
    await session()
