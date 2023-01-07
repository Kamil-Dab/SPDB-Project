from sqlalchemy import Column, Integer
from geoalchemy2 import Geometry

from .base import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geom_coords = Column(Geometry('POINT', srid=4326, spatial_index=True))
