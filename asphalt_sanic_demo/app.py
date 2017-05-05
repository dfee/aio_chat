import logging

from asphalt.core import ContainerComponent

from asphalt_sanic_demo.server import ServerComponent

logger = logging.getLogger(__name__)


class ApplicationComponent(ContainerComponent):
    def __init__(self, components):
        super().__init__(components)

    async def start(self, ctx):
        self.add_component('templating')
        self.add_component('server', ServerComponent)
        await super().start(ctx)
