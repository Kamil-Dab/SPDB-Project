from db.engine import get_session
from models import Road
from shapely.geometry import Point
from shapely.wkt import loads
from geoalchemy2.shape import from_shape
from sqlalchemy import func


class GeoRoad:
    def __init__(self, start_longitude, start_latitude, end_longitude, end_latitude):
        self.start_coord = Point(start_longitude, start_latitude)
        self.end_coord = Point(end_longitude, end_latitude)
        self.session = get_session()

    def get_nearest_start_point(self):
        return self.session.query(Road).order_by(func.ST_Distance(func.ST_StartPoint(Road.geom), from_shape(self.start_coord, srid=4326), True)).limit(1).one()

    def get_nearest_end_point(self):
        return self.session.query(Road).order_by(func.ST_Distance(func.ST_StartPoint(Road.geom), from_shape(self.end_coord, srid=4326), True)).limit(1).one()

    def shortest_path(self):
        QUERY_SHORTEST_PATH=  f"""SELECT agg_cost,
        CASE
            WHEN pt.node = rd.source THEN ST_AsText(geom)
            ELSE ST_AsText(ST_Reverse(geom))
        END AS geom
                FROM pgr_dijkstra(
                   'SELECT id, source, target, st_length(geom, true) as cost FROM roads',
                   {self.get_nearest_start_point().source},
                   {self.get_nearest_end_point().source},
                   false
                ) as pt
                JOIN roads rd ON pt.edge = rd.id
                ORDER BY seq;"""
        result = self.session.bind.execute(QUERY_SHORTEST_PATH).all()
        all_points = []
        self.path = []
        for row in result:
            self.path.append(row)
            all_points.extend(list(loads(row[-1]).coords))
        return all_points, result[-1][0]

    def point_in_path(self, distance):
        for iter in self.path:
            if iter[0] >= distance:
                return loads(iter[1]).coords[0]
        return []
