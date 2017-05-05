from typing import (
    ClassVar,
    Union,
)

from asphalt.core import Context
from sanic.request import Request


class ContextualRequest(Request):
    root_ctx: ClassVar[Union[Context, None]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx = Context(self.root_ctx)
        self.ctx.add_resource(self)
