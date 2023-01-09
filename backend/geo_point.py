from db.engine import get_session
from models import Poi
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from sqlalchemy import func




class GeoPoint:
    def __init__(self, latitude, longitude, amenity):
        self.coord = Point(longitude, latitude)
        self.amenity = amenity
        self.session = get_session()
    
    def buffor(self, distance):
        filter = from_shape(self.coord, srid=4326).ST_Transform(3857).ST_Buffer(distance)
        self.buffor_points = self.session.query(Poi).filter(Poi.amenity==self.amenity).filter(Poi.geom.ST_Intersects(filter)).subquery()
        return self.session.query(Poi).filter(Poi.amenity==self.amenity).filter(Poi.geom.ST_Intersects(filter)).all()
    
    def nearest_points(self, n):
        return self.session.query(self.buffor_points).order_by(func.ST_Distance(self.buffor_points.c.geom, from_shape(self.coord, srid=3857))).limit(n).all()