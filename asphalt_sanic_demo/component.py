import logging
import sqlite3

from asphalt.core import (
    CLIApplicationComponent,
    ContainerComponent,
)
from IPython import get_ipython

from .models import Base
from .server import ServerComponent
from .shell import Shell

logger = logging.getLogger(__name__)


class MasterStartMixin:
    async def start(self, ctx):
        self.add_component('templating')
        self.add_component('server', ServerComponent)
        self.add_component('sqlalchemy')
        await super().start(ctx)


class MasterComponent(MasterStartMixin, ContainerComponent):
    pass


class ShellComponent(MasterStartMixin, CLIApplicationComponent):
    async def run(self, ctx):
        shell = Shell(ctx)
        await shell.run()
        # Reconnect to prevent sqlite3 ProgrammingError
        # https://github.com/ipython/ipython/issues/680#issuecomment-2154854
        hist = get_ipython().history_manager
        hist.db = sqlite3.connect(hist.hist_file, check_same_thread=False)
