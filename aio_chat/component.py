import logging
import sqlite3


from asphalt.core import  (
    CLIApplicationComponent,
    ContainerComponent,
    Context,
    context_teardown,
)
from IPython import get_ipython

from .models import Base
from .pubsub import PubSubComponent
from .redis import RedisPoolComponent
from .server import ServerComponent
from .shell import Shell

logger = logging.getLogger(__name__)


class StartMixin:
    async def start(self, ctx):
        self.add_component('pubsub', PubSubComponent)
        self.add_component('redis', RedisPoolComponent)
        self.add_component('server', ServerComponent)
        self.add_component('sqlalchemy')
        self.add_component('templating')
        await super().start(ctx)

        # Set up tables
        async with Context(ctx) as subctx:
            Base.metadata.create_all(subctx.sql.bind)


class ApplicationComponent(StartMixin, ContainerComponent):
    pass


class ApplicationShellComponent(StartMixin, CLIApplicationComponent):
    async def run(self, ctx):
        shell = Shell(ctx)
        await shell.run()
        # Reconnect to prevent sqlite3 ProgrammingError
        # https://github.com/ipython/ipython/issues/680#issuecomment-2154854
        hist = get_ipython().history_manager
        hist.db = sqlite3.connect(hist.hist_file, check_same_thread=False)
