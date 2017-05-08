from asphalt.core import Context

async def context_middleware_factory(app, handler):
    async def middleware_handler(request):
        async with Context(app.ctx) as subctx:
            request.ctx = subctx
            return await handler(request)
    return middleware_handler
