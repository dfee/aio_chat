from sqlalchemy import (
    Column,
    Integer,
    String,
)

from .base import Base


class Friend(Base):
    __tablename__ = 'friends'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return '<{}(id={}, name={})>'.format(
            self.__class__.__name__,
            self.id,
            self.name,
        )
