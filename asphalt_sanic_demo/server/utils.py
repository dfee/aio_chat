import functools
import inspect

from asphalt.core import Context


def subcontext(fn):
    is_async = inspect.iscoroutinefunction(fn)
    @functools.wraps(fn)
    async def wrapper(request, *args, **kwargs):
        async with Context(request.app.ctx) as ctx:
            callable = functools.partial(fn, request, *args, ctx=ctx, **kwargs)
            result = await callable() if is_async else callable()
        return result
    return wrapper
