from sqlalchemy import Column, Integer, String, Numeric
from geoalchemy2 import Geometry

from .base import Base


class Hh2po4pgr(Base):
    __tablename__ = "hh_2po_4pgr"

    id = Column(Integer, primary_key=True, autoincrement=True)
    osm_id = Column(Integer)
    osm_name = Column(String)
    osm_meta = Column(String)
    osm_source_id = Column(Integer)
    osm_target_id = Column(Integer)
    clazz = Column(Integer)
    flags = Column(Integer)
    source = Column(Integer)
    target = Column(Integer)
    km = Column(Numeric(10, 2))
    kmh = Column(Integer)
    cost = Column(Numeric(10, 2))
    reverse_cost = Column(Numeric(10, 2))
    x1 = Column(Numeric(10, 2))
    y1 = Column(Numeric(10, 2))
    x2 = Column(Numeric(10, 2))
    y2 = Column(Numeric(10, 2))
    geom_way = Column(Geometry('LINESTRING'))