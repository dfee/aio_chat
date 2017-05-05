import functools
import inspect

from asphalt.core import Context


def contextualize(fn):
    @functools.wraps(fn)
    async def wrapper(request, *args, **kwargs):
        async with Context(request.app.ctx) as ctx:
            ctx.request = request
            retval = fn(ctx, *args, **kwargs)
            return (await retval) if inspect.isawaitable(retval) else retval

    return wrapper
