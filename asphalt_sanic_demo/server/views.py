import logging

from asphalt.core import (
    Context,
    executor,
)
import aiohttp
from aiohttp import web

from ..models import Message
from ..pubsub import PubSubMessage

logger = logging.getLogger(__name__)


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


class WebSocketView(web.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None

    @property
    def ctx(self):
        return self.request.ctx

    async def forward_psm(self, psm):
        assert isinstance(psm, PubSubMessage)
        message = {'text': psm.message.text}
        await self.ws.send_json(message)
        logger.info('Sent message: {}'.format(message))

    async def get(self):
        self.ws = web.WebSocketResponse()
        await self.ws.prepare(self.request)
        unsub = await self.ctx.pubsub.psubscribe('message:*', self.forward_psm)
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                async with Context(self.ctx) as subctx:
                    await add_message(subctx, msg.json()['text'])
            elif msg.type == aiohttp.WSMsgType.ERROR:
                await unsub()

        return self.ws


async def index(request):
    async with Context(request.ctx) as subctx:
        messages = await get_messages(subctx)
        text = await render_template(subctx, messages)
    response = web.Response()
    response.content_type = 'text/html'
    response.encoding = 'utf-8'
    response.text = text
    return response
