from db.engine import get_session
from models import Road
from shapely.geometry import Point
from shapely.wkt import loads
from geoalchemy2.shape import from_shape
from sqlalchemy import func
import random
import string


class GeoRoad:
    def __init__(self, start_longitude, start_latitude, end_longitude, end_latitude):
        self.start_coord = Point(start_longitude, start_latitude)
        self.end_coord = Point(end_longitude, end_latitude)
        self.session = get_session()
        self.table_name = self.get_random_table_name()

    def get_random_table_name(self, lenght=12):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(lenght))

    def get_nearest_start_point(self):
        return self.session.query(Road).order_by(func.ST_Distance(func.ST_StartPoint(Road.geom), from_shape(self.start_coord, srid=4326), True)).limit(1).one()

    def get_nearest_end_point(self):
        return self.session.query(Road).order_by(func.ST_Distance(func.ST_StartPoint(Road.geom), from_shape(self.end_coord, srid=4326), True)).limit(1).one()

    def shortest_path(self):
        QUERY_SHORTEST_PATH=  f"""
            DROP TABLE IF EXISTS {self.table_name};
            CREATE TABLE {self.table_name} AS
            SELECT agg_cost, cost as cost,
                CASE
                    WHEN pt.node = rd.source THEN geom
                    ELSE ST_Reverse(geom)
                END AS geom,
                CASE
                    WHEN pt.node = rd.source THEN ST_AsText(geom)
                    ELSE ST_AsText(ST_Reverse(geom))
                END AS geom_text
            FROM pgr_astar('
                SELECT id, source, target, st_length(geom, true) as cost,
                    st_x(st_startpoint(geom)) as x1,
                    st_y(st_startpoint(geom)) as y1,
                    st_x(st_endpoint(geom)) as x2,
                    st_y(st_endpoint(geom)) as y2   
                FROM roads',
                    {self.get_nearest_start_point().source},
                    {self.get_nearest_end_point().source},
                    false
                ) as pt
            JOIN roads rd ON pt.edge = rd.id 
            ORDER BY seq;
            SELECT * FROM {self.table_name};"""
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
