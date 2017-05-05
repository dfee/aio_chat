import logging

from asphalt.core import executor
from sanic import Sanic
from sanic.response import (
    html,
    redirect,
)
from sanic.views import HTTPMethodView

from ..models import Friend
from .request import ContextualRequest

logger = logging.getLogger(__name__)


server = Sanic(request_class=ContextualRequest)

class IndexView(HTTPMethodView):
    @executor
    def render_template(self, ctx, friends):
        '''
        Jinja2 reads from disk, thus blocking I/O.
        There is a configuraiton setting for Jinja2 to use an async mode,
        but asphalt-templating doesn't yet support it.
        '''
        return ctx.jinja2.render('index.html', friends=friends)

    @executor
    def get_friends(self, ctx):
        '''SQLAlchemy reads from disk, thus blocking I/O.'''
        friends = ctx.sql.query(Friend).all()
        # Important: when your models become more complex, you don't want to
        # issue further queries to load relationship data outside the executor.
        ctx.sql.expunge_all()
        return friends

    @executor
    def add_friend(self, ctx, name):
        '''SQLAlchemy reads from disk, thus blocking I/O.'''
        friend = Friend(name=name)
        ctx.sql.add(friend)
        ctx.sql.commit()

    async def get(self, request):
        friends = await self.get_friends(request.ctx)
        rendered = await self.render_template(request.ctx, friends)
        return html(rendered)

    async def post(self, request):
        name = request.form['name'][0]
        await self.add_friend(request.ctx, name)
        url = request.app.url_for(self.__class__.__name__)
        return redirect(url)

server.add_route(IndexView.as_view(), '/')
