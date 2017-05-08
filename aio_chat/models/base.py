from sqlalchemy.ext.declarative import declarative_base

from .metadata import metadata

Base = declarative_base(metadata=metadata)
