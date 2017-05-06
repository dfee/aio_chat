import logging

from asphalt.core import ContainerComponent

from .pubsub import PubSubComponent
from .server import ServerComponent

logger = logging.getLogger(__name__)


class MasterStartMixin:
    async def start(self, ctx):
        self.add_component('templating')
        self.add_component('server', ServerComponent)
        self.add_component('sqlalchemy')
        self.add_component('pubsub', PubSubComponent)
        await super().start(ctx)


class MasterComponent(MasterStartMixin, ContainerComponent):
    pass
