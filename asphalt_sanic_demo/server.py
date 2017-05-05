import asyncio
from datetime import datetime
import logging

from asphalt.core import Component
from asphalt.core.context import context_teardown
from sanic import Sanic
from sanic.response import html

logger = logging.getLogger(__name__)


app = Sanic()

@app.route("/")
async def index(request):
    ctx = request.app.ctx
    iso_now = datetime.now().isoformat()
    rendered = ctx.jinja2.render('index.html', now=iso_now)
    return html(rendered)


class ServerComponent(Component):
    def __init__(self, port=9001):
        self.port = port

    @context_teardown
    async def start(self, ctx):
        app.ctx = ctx
        ctx.add_resource(app, context_attr='server')
        task = ctx.loop.create_task(app.create_server(port=self.port))
        yield
        task.cancel()
