import logging

from asphalt.core import  (
    CLIApplicationComponent,
    ContainerComponent,
    Context,
    context_teardown,
)

from .models import Base
from .pubsub import PubSubComponent
from .redis import RedisPoolComponent
from .server import ServerComponent

logger = logging.getLogger(__name__)


class ApplicationStartMixin:
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


class ApplicationComponent(ApplicationStartMixin, ContainerComponent):
    pass