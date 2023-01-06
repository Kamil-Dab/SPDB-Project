const WARSAW_CORDS = [ 21.0122, 52.2297];

ol.proj.useGeographic();

const SELECTION = 'selection';
const START = 'START';
const END = 'END';
const ROUTE = 'ROUTE';
const POI = 'POI';

class InteractiveMap {
    constructor() {
        const mousePositionControl = new ol.control.MousePosition({
          coordinateFormat: ol.coordinate.createStringXY(4),
          projection: 'EPSG:4326',
          // comment the following two lines to have the mouse position
          // be placed within the map.
          className: 'custom-mouse-position',
          target: document.getElementById('mouse-position'),
        });

        this.marker_style = new ol.style.Style({
          text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            overflow: true,
            fill: new ol.style.Fill({
              color: '#000'
            }),
            stroke: new ol.style.Stroke({
              color: '#fff',
              width: 3
            }),
            offsetY: -12
          }),
          image: new ol.style.Icon({
            anchor: [0.5, 46],
            anchorXUnits: 'fraction',
            anchorYUnits: 'pixels',
            src: '/static/marker',
            scale: 0.1
          })
        });

        this.route_style = new ol.style.Style({
            stroke: new ol.style.Stroke({
                width: 6, color: [40, 40, 40, 0.8]
            }),
        });

        this.vectorSource = new ol.source.Vector({});
        this.vectorLayer = new ol.layer.Vector({
            target: 'points',
            source: this.vectorSource,
            style: (feature) => {
                if (feature.get('type') == ROUTE) {
                    return this.route_style;
                } else {
                    this.marker_style.getText().setText(feature.get('text'))
                    return this.marker_style;
                }
            }
        })

        this.map = new ol.Map({
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                }),
                this.vectorLayer,
            ],
            target: 'map',
            view: new ol.View({
                center: WARSAW_CORDS,
                zoom: 10
            }),
            controls: [mousePositionControl]
        });

        this.map.on('click', (e) => {
            let [ lon, lat ] = e.coordinate;
            this.select_point(lon, lat, SELECTION);
        });

        this.selected_point = null;
        this.start_point = null;
        this.end_point = null;
    }

    clear_features(type) {
        this.vectorSource.forEachFeature((f) => {
            if (f.get('type') === type) {
                this.vectorSource.removeFeature(f);
            }
        })
    }

    select_point(lon, lat, type, text) {
        this.clear_features(type);
        let feature = new ol.Feature({
            geometry: new ol.geom.Point([ lon, lat ]),
            text: text !== undefined ? text : '',
            type: type,
        })
        this.vectorSource.addFeature(feature);
        this.selected_point = {
            lon: lon,
            lat: lat
        };
    }

    select_route(cords) {
        this.clear_features(ROUTE);
        let feature = new ol.Feature({
            geometry: new ol.geom.LineString(cords),
            text: '',
            type: ROUTE
        });
        this.vectorSource.addFeature(feature);
    }

    select_pois(pois) {
        this.clear_features(POI);
        pois.forEach((p) => {
            this.select_point(p.lon, p.lat, POI, p.name);
        })
    }

    set_selected_point_as_start() {
        if (this.selected_point !== null) {
            this.clear_features(SELECTION);
            this.clear_features(START);
            this.select_point(this.selected_point.lon, this.selected_point.lat, START, 'Start');
            this.start_point = this.selected_point;
            this.selected_point = null;
        }
    }

    set_selected_point_as_end() {
        if (this.selected_point !== null) {
            this.clear_features(SELECTION);
            this.clear_features(END);
            this.select_point(this.selected_point.lon, this.selected_point.lat, END, 'End');
            this.end_point = this.selected_point;
            this.selected_point = null;
        }
    }

    replace_start_end() {
        let start = this.end_point;
        let end = this.start_point;

        if (start !== null && end !== null) {
            if (start !== null) {
                this.clear_features(START);
                this.select_point(start.lon, start.lat, START, 'Start');
            }

            if (end !== null) {
                this.clear_features(END);
                this.select_point(end.lon, end.lat, END, 'End');
            }

            this.start_point = start;
            this.end_point = end;
        }
    }

    reset() {
        this.vectorSource.clear();
        this.start_point = null;
        this.end_point = null;
        this.selected_point = null;
    }
}

class POIManager {
    constructor() {
        this.available = [];
        this.selected = [];
    }

    filter_duplicates() {
        this.available = this.available.filter((i) => !this.selected.find((j) => j.name === i.name));
    }

    set_avaialble(available) {
        this.available = available;
        this.filter_duplicates();
        this.update_available_pois();
    }

    update_available_pois() {
        let html = this.available.map((p, index) =>
`
<li> <label> ${p.name} </label> <button type="button" onclick="addPOI(${index})" class="btn btn-primary m-3"> Dodaj </button> </li>
`
        ).join("\n");
        $('#available_POI_list').html(html);
    }

    update_selected_pois() {
        let html = this.selected.map((p, index) =>
`
<li> <label> ${p.name} </label> <button type="button" onclick="removePOI(${index})" class="btn btn-danger m-3"> Usuń </button> </li>
`
        )
        $('#selected_POI_list').html(html);
    }

    add_poi(index) {
        let poi = this.available.at(index);
        this.available = this.available.filter((item) => item !== poi);
        this.selected.push(poi);
        this.filter_duplicates();
        this.update_selected_pois();
        this.update_available_pois();
    }

    remove_poi(index) {
        let poi = this.selected.at(index);
        this.selected = this.selected.filter((item) => item !== poi);
        this.available.push(poi);
        this.filter_duplicates();
        this.update_selected_pois();
        this.update_available_pois();
    }

    selected_pois() {
        return this.selected;
    }

    reset() {
        this.selected = [];
        this.available = [];
        this.update_selected_pois();
        this.update_available_pois();
    }
}

class PointChooser {
    constructor() {
        this.points = [];
    }

    choose_points(points) {
        this.points = points;

        let html = points.map((p, index) =>
`
<li> <button type="button" class="btn btn-info" onclick="modalChoosePoint(${index})"> ${p.name} </button> </li>
`
        ).join("\n");
        $('#pointSelector').html(html);
        $('#modal').modal('show');
    }

    select_point(index) {
        $('#modal').modal('hide');
        let point = this.points.at(index);
        map.select_point(point.lon, point.lat, SELECTION, point.name);
    }

    reset() {
        this.points = [];
    }
}


const map = new InteractiveMap();
const poi = new POIManager();
const chooser = new PointChooser();

const fetchRoute = async (data) => {
    return await fetch("/route", {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

const fetchPointByName = async (name) => {
    return await fetch("/point/byName?" + new URLSearchParams({ name: name }), {
        method: "GET",
    });
}

const fetchPointByCords = async (lon, lat) => {
    return await fetch("/point/byCords?" + new URLSearchParams({ lon: lon, lat: lat }), {
        method: "GET"
    });
}

window.searchPointByName = (name) => {
    fetchPointByName(name)
        .catch((e) => console.log(e))
        .then(resp => resp.json())
        .then(objs => {
            chooser.choose_points(objs.points);
        });
}

window.searchPointByCords = (lon, lat) => {
    fetchPointByCords(parseFloat(lon), parseFloat(lat))
        .catch((e) => console.log(e))
        .then((resp) => resp.json())
        .then((objs) => {
            chooser.choose_points(objs.points);
        });
}

window.setAsStart = () => { map.set_selected_point_as_start() }
window.setAsEnd = () => { map.set_selected_point_as_end() }
window.replaceStartEnd = () => { map.replace_start_end() }

window.resetMap = () => {
    map.reset();
    poi.reset();
    chooser.reset();
}

window.findRoute = (enlen, searchStart) => {
    fetchRoute({
        enlen: parseFloat(enlen),
        searchStart: parseFloat(searchStart),
        start: map.start_point,
        end: map.end_point,
        pois: poi.selected_pois()
    })
        .catch((e) => console.log(e))
        .then((resp) => resp.json())
        .then((obj) => {
            map.select_route(obj.route);
            poi.set_avaialble(obj.pois);
            map.select_pois(obj.pois);
        });
}

window.addPOI = (index) => { poi.add_poi(index); }
window.removePOI = (index) => { poi.remove_poi(index); }
window.modalChoosePoint = (index) => { chooser.select_point(index); }
