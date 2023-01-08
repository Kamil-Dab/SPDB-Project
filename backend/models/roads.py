from sqlalchemy import Column, Integer
from geoalchemy2 import Geometry

from .base import Base


class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Integer)
    target = Column(Integer)
    geom = Column(Geometry('LINESTRING'))