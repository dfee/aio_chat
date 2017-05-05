import asyncio
import logging
from typing import (
    ClassVar,
    Union,
)

from asphalt.core import Context
from sanic.request import Request

logger = logging.getLogger(__name__)


class ContextualRequest(Request):
    parent_ctx: ClassVar[Union[Context, None]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx = Context(self.parent_ctx)

    def __del__(self):
        asyncio.ensure_future(self.ctx.close())
