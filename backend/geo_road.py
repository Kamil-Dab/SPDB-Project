from db.engine import get_session
from models import Hh2po4pgr
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from sqlalchemy import func




class GeoRoad:
    def __init__(self, start_latitude, start_longitude, end_latitude, end_longitude):
        self.start_coord = Point(start_longitude, start_latitude)
        self.end_coord = Point(end_longitude, end_latitude)
        self.session = get_session()
    
    def get_nearest_start_point(self):
        NEAREST_START_POINT_QUERY = f"""SELECT t.target, ST_SetSrid(ST_MakePoint(t.x1, t.y1), 
                                    4326) FROM (SELECT target, x1, y1 FROM hh_2po_4pgr 
                                    ORDER BY ST_Distance(ST_MakePoint(x1, y1), '{self.start_coord}')
                                    LIMIT 1) as t;"""
        return self.session.bind.execute(NEAREST_START_POINT_QUERY)

    def get_nearest_end_point(self, x, y):
        NEAREST_END_POINT_QUERY = f"""SELECT t.target, ST_SetSrid(ST_MakePoint(t.x2, t.y2), 
                                    4326) FROM (SELECT target, x2, y2 FROM hh_2po_4pgr 
                                    ORDER BY ST_Distance(ST_MakePoint(x2, y2), '{self.end_coord}')
                                    LIMIT 1) as t;"""
        return self.session.bind.execute(NEAREST_END_POINT_QUERY)

    def test(self):
        TEST=  "SELECT geom_way, km / kmh as time FROM pgr_dijkstra('" \
                "SELECT id, source, target, km as cost FROM hh_2po_4pgr', " \
                "1, 5000, false) AS pt JOIN hh_2po_4pgr as rd " \
                "ON (pt.edge = rd.id) ORDER BY seq;"
        return self.session.bind.execute(TEST)

    # def shortest_path(self):
    #     return self.session.query(func.ST_Length(func.ST_ShortestLine(Hh2po4pgr.geom_way, from_shape(self.start_coord, srid=4326), from_shape(self.end_coord, srid=4326))))
    