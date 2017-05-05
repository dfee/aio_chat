import asyncio
import functools
from types import ModuleType

from IPython import start_ipython
from asphalt.core import (
    CLIApplicationComponent,
    executor,
    run_application,
)
from asphalt.core.utils import merge_config
import click
from ruamel import yaml
from traitlets.config.loader import Config

from asphalt_sanic_demo.server import ServerComponent


class Shell:
    def __init__(self, ctx):
        self.ctx = ctx

    def run_on_loop(self, co):
        return asyncio.run_coroutine_threadsafe(co, self.ctx.loop)

    @property
    def user_ns(self):
        return {
            'loop': self.ctx.loop,
            'run_on_loop': self.run_on_loop,
            'redis': self.ctx.redis,
            'jinja2': self.ctx.jinja2,
            'server': self.ctx.server,
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

class ShellComponent(CLIApplicationComponent):
    def __init__(self, components):
        super().__init__(components)

    async def start(self, ctx):
        self.add_component('redis')
        self.add_component('server', ServerComponent)
        self.add_component('templating')
        await super().start(ctx)

    async def run(self, ctx):
        print('here', flush=True)
        shell = Shell(ctx)
        await shell.run()


@click.command(help='Run a shell in the context of the application.')
@click.argument('configfile', type=click.File(), nargs=-1, required=True)
@click.option(
    '--unsafe',
    is_flag=True,
    default=False,
    help='use unsafe mode when loading YAML (enables markup extensions)'
)
def main(configfile, unsafe):
    config = {}
    for path in configfile:
        config_data = yaml.load(path) if unsafe else yaml.safe_load(path)
        assert isinstance(config_data, dict), \
            'the document root element must be a dictionary'
        config = merge_config(config, config_data)

    xshell_component = ShellComponent(config['component']['components'])
    run_application(xshell_component)

if __name__ == '__main__':
    main()
