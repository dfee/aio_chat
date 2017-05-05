import logging

from asphalt.core import executor
from sanic import Sanic
from sanic.response import (
    html,
    redirect,
)

from ..models import Friend
from .utils import contextualize

logger = logging.getLogger(__name__)
server = Sanic()

@executor
def render_template(ctx, friends):
    '''
    Jinja2 reads from disk, thus blocking I/O.
    There is a configuraiton setting for Jinja2 to use an async mode,
    but asphalt-templating doesn't yet support it.
    '''
    return ctx.jinja2.render('index.html', friends=friends)

@executor
def get_friends(ctx):
    '''SQLAlchemy reads from disk, thus blocking I/O.'''
    friends = ctx.sql.query(Friend).all()
    # Important: when your models become more complex, you don't want to
    # issue further queries to load relationship data outside the executor.
    ctx.sql.expunge_all()
    return friends

@executor
def add_friend(ctx, name):
    '''SQLAlchemy reads from disk, thus blocking I/O.'''
    friend = Friend(name=name)
    ctx.sql.add(friend)

@server.route('/', methods=['GET'])
@contextualize
async def get_index(ctx):
    friends = await get_friends(ctx)
    rendered = await render_template(ctx, friends)
    return html(rendered)

@server.route('/', methods=['POST'])
@contextualize
async def post_index(ctx):
    name = ctx.request.form['name'][0]
    await add_friend(ctx, name)
    url = ctx.request.app.url_for('get_index')
    return redirect(url)
