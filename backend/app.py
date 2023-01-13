from flask import Flask, render_template, request, session
from flask.helpers import abort, send_file
from geo_point import GeoPoint
from geo_road import GeoRoad
import numpy as np
from typing import Dict, List, Tuple

app = Flask(__name__)
app.secret_key = 'iwhfwuhuehufewhfufhfuewheuh'

@app.route("/")
def index():
    return render_template('index.html')

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
    def __init__(self, start: Dict, stop: Dict, vias: List[Dict], enlen: float, searchst: float) -> None:
        self.start = start
        self.stop = stop
        self.vias = vias
        self.enlen = enlen
        self.searchst = searchst
        self.routes = []
        self.availabla_vias = []

    def find_route(self):
        if not self.vias:
            road = GeoRoad(self.start['lon'], self.start['lat'], self.stop['lon'], self.stop['lat'])
            print("Routing...")
            path, length = road.shortest_path()
            print("Finding start point...")
            stlon, stlat = road.point_in_path(self.searchst)
            point = GeoPoint().nearest_points(stlon, stlat, 3, self.enlen)

            # TODO: if not found:

            self.availabla_vias = [ { 'name': i[1], 'lon': i[0][1], 'lat': i[0][0] } for i in point ]

            self.routes.append(([], path))

            return path, self.availabla_vias

    def set(self, start, stop, vias, enlen, searchst):
        self.start = start
        self.stop = stop
        self.vias = vias
        self.enlen = enlen
        self.searchst = searchst


ROUTE: Route | None = None

@app.route('/route', methods = ["POST"])
def route():
    try:
        params = request.json

        start = params['start']
        end = params['end']
        enlen = float(params['enlen']) * 1000 # Maksymalne wydłużenie
        searchStart = float(params['searchStart']) * 1000
        selected_pois = params['pois']

        # TODO:
        global ROUTE
        if ROUTE is None:
            ROUTE = Route(start, end, selected_pois, enlen, searchStart)
        else:
            ROUTE.set(start, end, selected_pois, enlen, searchStart)

        route, pois = ROUTE.find_route()

        return { 'route': route, 'pois': pois }
    except:
        raise
        return abort(400)
