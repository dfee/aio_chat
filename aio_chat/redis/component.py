import logging
from ssl import SSLContext

from aioredis import create_pool
from asphalt.core import context_teardown
from asphalt.redis.component import RedisComponent

logger = logging.getLogger(__name__)


class RedisPoolComponent(RedisComponent):
    @context_teardown
    async def start(self, ctx):
        clients = []  # actually, a collection of pools
        for resource_name, context_attr, config in self.clients:
            # Resolve resource references
            if isinstance(config['ssl'], str):
                config['ssl'] = await ctx.request_resource(
                    SSLContext,
                    config['ssl']
                )

            pool = await create_pool(**config)
            clients.append((resource_name, pool))
            ctx.add_resource(pool, resource_name, context_attr)
            logger.info(
                'Configured Redis pool (%s / ctx.%s; address=%s, db=%d)',
                resource_name,
                context_attr,
                config['address'],
                config['db'],
            )

        yield

        for resource_name, pool in clients:
            pool.close()
            await pool.wait_closed()
            logger.info('Redis client (%s) shut down', resource_name)

