from db.engine import get_session
from models import Poi
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from sqlalchemy import func
from pyproj import Proj, transform


class GeoPoint:
    def __init__(self):
        self.session = get_session()
        self.inProj = Proj('epsg:3857')
        self.outProj = Proj('epsg:4326')
    
    def nearest_points(self, longitude, latitude, n, distance=5000):
        coord = Point(longitude, latitude)
        filter = from_shape(coord, srid=4326).ST_Transform(3857).ST_Buffer(distance)
        buffor_points = self.session.query(Poi).filter(Poi.geom.ST_Intersects(filter)).subquery()
        points = self.session.query(buffor_points).order_by(func.ST_Distance(buffor_points.c.geom, from_shape(coord, srid=3857))).limit(n).all()
        return [[transform(self.inProj, self.outProj, *k.get_coords()), k.name] for k in points]

    def nearest_points_by_name(self, name, n):
        points = self.session.query(Poi).order_by(func.difference(Poi.name, name).desc(),func.levenshtein(Poi.name, name)).limit(n).all()
        inProj = Proj('epsg:3857')
        outProj = Proj('epsg:4326')
        return [[transform(self.inProj, self.outProj, *k.get_coords()), k.name] for k in points]
