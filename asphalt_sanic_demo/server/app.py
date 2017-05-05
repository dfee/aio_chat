from datetime import datetime
import logging

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
