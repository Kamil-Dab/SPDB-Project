from flask import Flask, render_template, request, session
from flask.helpers import abort, send_file
from geo_point import GeoPoint
from geo_road import GeoRoad
import numpy as np
from typing import Dict, List, Tuple
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'dwqidhwqudwhduwqhdu'

POI_TYPES = [
    'ALL',
    'fast_foos',
    'parking',
    'fast_food',
    'food_court',
    'police',
    'restaurant',
    'healthcare',
    'feeding_place',
    'bar',
    'hospital',
    'pub',
    'fuel',
    'toilets',
    'marketplace',
    'car_wash',
    'pharmacy',
    'ice_cream',
]
POI_TYPES.sort()

@app.route("/")
def index():
    return render_template('index.html', poi_types=POI_TYPES)

@app.route('/static/main')
def mainjs():
    return send_file("static/main.js")

@app.route('/static/marker')
def marker():
    return send_file('static/marker.jpg')

@app.route('/point/byName')
def pointByName():
    try:
        name = request.args.get('name')
        n = request.args.get('n', 50)
        points = GeoPoint().nearest_points_by_name(name, n)

        return {
            'points': [ { 'name': i[1], 'lon': i[0][1], 'lat': i[0][0] } for i in points ]
        }
    except:
        return abort(400)

@app.route('/point/byCords')
def pointByCords():
    try:
        lon = float(request.args.get("lon"))
        lat = float(request.args.get("lat"))
        n = request.args.get('n', 50)
        points = GeoPoint().nearest_points(lon, lat, n)

        return {
            'points': [ { 'name': i[1], 'lon': i[0][1], 'lat': i[0][0] } for i in points ]
        }
    except:
        return abort(400)

class Route:
    def __init__(self, start: Dict, stop: Dict, vias: List[Dict], enlen: float, searchst: float, n: int, poi_filter: str) -> None:
        self.start = start
        self.stop = stop
        self.vias = vias
        self.enlen = enlen
        self.searchst = searchst
        self.availabla_vias = []
        self.n = n
        self.poi_filter = poi_filter
        self.cache = []
        self.cache2 = []

    def find_route(self):
        if not self.vias:
            return self._find_route_and_poi_points(self.start, self.stop, self.enlen, self.searchst)
        else:
            return self._find_route_via_poi_points(self.start, self.stop, self.vias)

    def _find_route_and_poi_points(self, start, stop, enlen, searchst):
        for a, b in self.cache2:
            if a == (start, stop, enlen, searchst, self.poi_filter):
                self.availabla_vias = b[2]
                return b

        road = GeoRoad(start['lon'], start['lat'], stop['lon'], stop['lat'])
        print("Routing...")
        path, length = road.shortest_path()
        print("Finding start point...")
        points = self._find_possible_points(road, length, searchst, enlen, 3 * self.n)

        # TODO: if not found:

        self.availabla_vias = self._filter_poi_points(start, stop, points, enlen, length, self.n)
        self.cache2.append([(start, stop, enlen, searchst, self.poi_filter), (path, length, self.availabla_vias)])

        return path, length, self.availabla_vias

    def _find_route_via_poi_points(self, start, stop, pois):
        for a, b in self.cache:
            if a == (start, stop, pois):
                return b[0], b[1], self.availabla_vias

        fragments = [ GeoRoad(i['lon'], i['lat'], j['lon'], j['lat']).shortest_path() for i, j in zip([ start ] + pois, pois + [ stop ]) ]

        road = []
        length = 0
        for el_path, el_len in fragments:
            road.extend(el_path)
            length += el_len

        self.cache.append([(start, stop, pois), (road, length)])

        return road, length, self.availabla_vias

    def _filter_poi_points(self, start, stop, pois, enlen, cur_len, n):
        good_points = []

        for poi in pois:
            point = { 'name': poi[1], 'lon': poi[0][1], 'lat': poi[0][0] }
            _, length, _ = self._find_route_via_poi_points(start, stop, [ point ])

            if length - cur_len <= enlen:
                good_points.append(point)

            if len(good_points) >= n:
                break

        return good_points

    def _find_possible_points(self, geo_road, total_len, srst, enlen, n):
        points = []

        d = srst
        while d < total_len and len(points) < n:
            stlon, stlat = geo_road.point_in_path(d)
            p = GeoPoint().nearest_points(stlon, stlat, n, enlen, self.poi_filter)
            points.extend(p)

            d += enlen

        return points


    def setState(self, state):
        self.availabla_vias = state['availabla_vias']
        self.cache = state['cache']
        self.cache2 = state['cache2']

    def getState(self):
        return {
            'availabla_vias': self.availabla_vias,
            'cache': self.cache,
            'cache2': self.cache2
        }

CACHE = {}

@app.route('/route', methods = ["POST"])
def route():
    try:
        params = request.json

        start = params['start']
        end = params['end']
        enlen = float(params['enlen']) * 1000 # Maksymalne wydłużenie
        searchStart = float(params['searchStart']) * 1000
        selected_pois = params['pois']
        poi_n = int(params['poi_n'])
        poi_filter = params['poi_filter']

        if poi_filter == "ALL":
            poi_filter = None

        road = Route(start, end, selected_pois, enlen, searchStart, poi_n, poi_filter)

        if "road" in session:
            state = session.get("road")
            if state in CACHE:
                road.setState(CACHE[state])

        route, length, pois = road.find_route()

        id = str(uuid4())
        session['road'] = id
        CACHE[id] = road.getState()

        return { 'route': route, 'pois': pois, 'length': length / 1000 }
    except Exception as e:
        print(e)
        return abort(400)
