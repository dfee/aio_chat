import inflection
from sqlalchemy import (
    Column,
    Integer,
    String,
    event,
)
from sqlalchemy.orm.session import object_session

from .base import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    text = Column(String)

    @property
    def __pubsub_id__(self):
        return '{}:{}'.format(
            inflection.underscore(self.__class__.__name__),
            self.id,
        )

@event.listens_for(Message, 'after_insert')
def receive_after_insert(mapper, connection, target):
    sql = object_session(target)
    ctx = sql.info['ctx']
    ctx.call_async(ctx.pubsub.publish, target.__pubsub_id__, target)
