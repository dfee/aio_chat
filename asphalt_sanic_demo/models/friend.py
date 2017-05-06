import json

import inflection
from sqlalchemy import (
    Column,
    Integer,
    String,
    event,
)
from sqlalchemy.orm.session import object_session

from .base import Base


class Friend(Base):
    __tablename__ = 'friends'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    @property
    def __pubsub_id__(self):
        return '{}:{}'.format(
            inflection.underscore(self.__class__.__name__),
            self.id,
        )

    def __repr__(self):
        return '<{}(id={}, name={})>'.format(
            self.__class__.__name__,
            self.id,
            self.name,
        )

@event.listens_for(Friend, 'after_insert')
def receive_after_insert(mapper, connection, target):
    sql = object_session(target)
    ctx = sql.info['ctx']

    fields = ['id', 'name']
    data = {field: getattr(target, field) for field in fields}
    ctx.call_async(
        ctx.pubsub.publish,
        target.__pubsub_id__,
        json.dumps(data),
    )
