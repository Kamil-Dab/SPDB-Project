from db.engine import get_session
from models import Location
from shapely.geometry import Point
from geoalchemy2.shape import from_shape, to_shape
from random import randint
from sqlalchemy import func




class GeoPoint:
    def __init__(self, latitude, longitude):
        self.coord = Point(longitude, latitude)
        self.session = get_session()
    
    def buffor(self, distance):
        filter = from_shape(self.coord, srid=4326).ST_Transform(3857).ST_Buffer(distance).ST_Transform(4326)
        self.buffor_points = self.session.query(Location).filter(Location.geom_coords.ST_Intersects(filter)).subquery()
        return self.session.query(Location).filter(Location.geom_coords.ST_Intersects(filter)).all()
    
    def add(self):
        location = Location(id=randint(0,1000), geom_coords=from_shape(self.coord, srid=4326))
        self.session.add(location)
        self.session.commit()
    
    def nearest_points(self, n):
        return self.session.query(self.buffor_points).order_by(func.ST_Distance(self.buffor_points.c.geom_coords, from_shape(self.coord, srid=4326))).limit(n).all()