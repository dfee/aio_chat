from datetime import datetime
import logging

from sanic import Sanic
from sanic.response import html

from .request import ContextualRequest

logger = logging.getLogger(__name__)


app = Sanic(request_class=ContextualRequest)

@app.route("/")
async def index(request):
    rendered = request.ctx.jinja2.render(
        'index.html',
        now=datetime.now().isoformat(),
    )
    return html(rendered)
