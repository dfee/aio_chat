import asyncio
from types import ModuleType

from IPython import start_ipython
from asphalt.core import executor
from traitlets.config.loader import Config

import aio_chat.models


class Shell:
    def __init__(self, ctx):
        self.ctx = ctx

    @property
    def user_ns(self):
        return {
            '_m': aio_chat.models,
            'ctx': self.ctx,
            'call_async': self.ctx.call_async,
            'loop': self.ctx.loop,
            'jinja2': self.ctx.jinja2,
            'pubsub': self.ctx.pubsub,
            'redis': self.ctx.redis,
            'server': self.ctx.server,
            'sql': self.ctx.sql,
        }

    @property
    def banner2(self):
        banner = 'Environment:\n'
        for k, v in self.user_ns.items():
            if isinstance(v, ModuleType):
                name = v.__name__
            else:
                name = v.__module__
            banner += '\t{0:16}{1}\n'.format(k, name)
        return banner

    @property
    def config(self):
        config = Config()
        config.TerminalInteractiveShell.banner2 = self.banner2
        return config

    @executor
    def run(self):
        start_ipython(
            argv=[],
            user_ns=self.user_ns,
            config=self.config,
        )
