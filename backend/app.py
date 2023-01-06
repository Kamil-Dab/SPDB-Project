from flask import Flask, render_template, request
from flask.helpers import abort, send_file

app = Flask(__name__)

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
    # TODO:
    try:
        name = request.args.get('name')

        return {
            'points': [ {'name': name, 'lon': 20.98, 'lat': 52.29 } ] # Kordynaty jakiegoś kawałka Wawy do testów
        }
    except:
        return abort(400)

@app.route('/point/byCords')
def pointByCords():
    # TODO:
    try:
        lon = request.args.get("lon")
        lat = request.args.get("lat")

        return {
            'points': [ { 'name': 'XD', 'lon': lon, 'lat': lat } ]
        }
    except:
        return abort(400)


@app.route('/route', methods = ["POST"])
def route():
    try:
        params = request.json

        start = params['start']
        end = params['end']
        enlen = params['enlen'] # Maksymalne wydłużenie
        searchStart = params['searchStart']
        selected_pois = params['pois']

        # TODO:
        route = [ [start['lon'], start['lat']], [ end['lon'], end['lat'] ] ]

        if len(selected_pois) == 1:
            route.append([selected_pois[0]['lon'], selected_pois[0]['lat']])

        pois = [ { 'name': 'JAKIŚ CHIŃCZYL', 'lon': 20.77, 'lat': 52.11 } ]
        return { 'route': route, 'pois': pois }
    except:
        return abort(400)
