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
        QUERY_SHORTEST_PATH=  f"""SELECT ST_AsText(geom)
                FROM pgr_dijkstra(
                   'SELECT id, source, target, st_length(geom, true) as cost FROM roads',
                   {self.get_nearest_start_point().source},
                   {self.get_nearest_end_point().source},
                   false
                ) as pt
                JOIN roads rd ON pt.edge = rd.id ;"""
        result = self.session.bind.execute(QUERY_SHORTEST_PATH).all()
        convert_result = [[*row[:-1], list(loads(row[-1]).coords)] for row in result]
        return convert_result

    def point_in_path(self, distance):
        QUERY_POINT_IN_PATH = f"""
            SELECT
                ST_X(ST_LineInterpolatePoint(geom, procentage_left)) as x,
                ST_Y(ST_LineInterpolatePoint(geom, procentage_left)) as y
            FROM
            (
                SELECT
                    seq, node, edge, cost as cost, agg_cost, geom,
                    ({distance} - agg_cost)/cost as procentage_left
                FROM pgr_dijkstra(
                    'SELECT id, source, target, st_length(geom, true) as cost FROM roads',
                    {self.get_nearest_start_point().source},
                    {self.get_nearest_end_point().target},
                    false
                ) as pt
                JOIN roads rd ON pt.edge = rd.id
                WHERE pt.agg_cost <= {distance}
                ORDER BY agg_cost DESC LIMIT 1
            ) as foo;
        """
        point = self.session.bind.execute(QUERY_POINT_IN_PATH).all()
        if not point:
            return []

        return point[0][:]
