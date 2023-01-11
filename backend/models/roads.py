from sqlalchemy import Column, Integer
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from .base import Base


class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Integer)
    target = Column(Integer)
    geom = Column(Geometry('LINESTRING'))

    def get_coords(self):
        shply_geom = to_shape(self.geom)
        return list(shply_geom.coords)