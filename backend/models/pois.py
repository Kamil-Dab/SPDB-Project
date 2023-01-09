from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry

from .base import Base


class Poi(Base):
    __tablename__ = "pois"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amenity = Column(String)
    name = Column(String)

    geom = Column(Geometry('POINT', srid=4326, spatial_index=True))
