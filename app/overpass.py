import json
import math

import osm2geojson
import requests
from shapely.geometry import mapping, Point

from cache import Cache

ZOOM_DEFAULT = 16


class OverpassClient:
    def __init__(self, server, user_agent, cache_dir, cache_days, cache_size):
        self.server = server
        self.user_agent = user_agent
        self.cache = Cache(cache_dir, cache_days, cache_size)
        # using tag selection from https://github.com/microsoft/soundscape/blob/main/svcs/data/soundscape/other/mapping.yml
        with open("osm_tags.json") as f:
            self.tags = json.load(f)

    def _build_query(self, ax, ay, bx, by):
        """Generate an Overpass query that is the union of all tags we are
        matching. It will look something like (shortened for brevity):

            [out:json][bbox:34.873928539,-77.835639,38.267204,-74.49514];
            (
                nwr[amenity];
                nwr[building];
                nwr[entrance];
                nwr[railway~'station|subway_entrance|tram_stop'];
            );
            out geom;

        This roughly translates to: In JSON format, limited to a specific
        bounding box, find all nodes/ways/relations with the specified tags,
        with the specified values when given, and include the geometry
        information.
        """
        q = ""
        for tag, values in self.tags.items():
            if len(values) > 0:
                q += f"nwr[{tag}~'{'|'.join(values)}'];\n"
            else:
                q += f"nwr[{tag}];\n"
        return f"""[out:json][bbox:{ax},{ay},{bx},{by}];
        (
            {q}
        );
        out geom;"""

    def _execute_query(self, q):
        # TODO check response
        response = requests.get(
            self.server,
            params={"data": q},
            headers={"User-Agent": self.user_agent},
        )
        return response.json()

    def item_to_soundscape_geojson(self, item):
        """Description of format at
        https://github.com/steinbro/soundscape/blob/main/docs/services/data-plane-schema.md
        """
        # primary tag (at least one should exist, because it was included
        # in the results)
        feature_type, feature_value = [
            (k, v) for (k, v) in item["properties"]["tags"].items() if k in self.tags
        ][0]

        return {
            "feature_type": feature_type,
            "feature_value": feature_value,
            "geometry": item["geometry"],
            "osm_ids": [item["properties"]["id"]],
            "properties": item["properties"]["tags"],
            "type": "Feature",
        }

    def compute_intersections(self, shapes_json):
        """Find all points that are shared by more than one road.

        Replicates intersection determination from
        https://github.com/microsoft/soundscape/blob/main/svcs/data/tilefunc.sql#L21
        """
        point_to_osm_ids = {}
        for item in shapes_json:
            if (
                item["shape"].geom_type == "LineString"
                and "highway" in item["properties"]["tags"]
            ):
                for point in mapping(item["shape"])["coordinates"]:
                    point_to_osm_ids.setdefault(point, []).append(
                        item["properties"]["id"]
                    )

        for p, oids in point_to_osm_ids.items():
            if len(oids) > 1:
                yield {
                    "feature_type": "highway",
                    "feature_value": "gd_intersection",
                    "geometry": mapping(Point(p)),
                    "osm_ids": oids,
                    "properties": {},
                    "type": "Feature",
                }

    def overpass_to_soundscape_geojson(self, overpass_json):
        """Use osm2geojson to handle the nontrivial type coversion from OSM
        nodes/ways/relations to GeoJSON points/polygons/multipolygons/etc.
        """
        # TODO add entrances
        geojson = osm2geojson.json2geojson(overpass_json)
        shapes_json = osm2geojson.json2shapes(overpass_json)
        features = list(
            self.item_to_soundscape_geojson(item) for item in geojson["features"]
        ) + list(self.compute_intersections(shapes_json))
        return {
            "features": features,
            "type": "FeatureCollection",
        }

    def query(self, x, y):
        coords = tile_bbox_from_x_y(x, y)
        return self.cache.get(f"{x}_{y}", lambda: self.query_coords(*coords))

    def query_coords(self, ax, ay, bx, by):
        q = self._build_query(ax, ay, bx, by)
        data = self._execute_query(q)
        return self.overpass_to_soundscape_geojson(data)


# from https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
# This returns the NW-corner of the square. Use the function with xtile+1 and/or ytile+1 to get the other corners. With xtile+0.5 & ytile+0.5 it will return the center of the tile.
def num2deg(xtile, ytile, zoom):
    n = 2.0**zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


# replicating https://github.com/mapbox/postgis-vt-util/blob/master/src/TileBBox.sql
def tile_bbox_from_x_y(x, y, zoom=ZOOM_DEFAULT):
    ax, ay = num2deg(x, y, zoom)
    bx, by = num2deg(x + 1, y + 1, zoom)
    tile_minx = min(ax, bx)
    tile_maxx = max(ax, bx)
    tile_miny = min(ay, by)
    tile_maxy = max(ay, by)
    return (tile_minx, tile_miny, tile_maxx, tile_maxy)
