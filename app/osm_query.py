import math
import requests

OVERPASS_API_URL = "http://overpass-api.de/api/interpreter"
# OVERPASS_API_URL = "https://overpass.kumi.systems/api/interpreter/"


def query(ax, ay, bx, by):
    # TODO expand matched nodes
    q = f"""[out:json];
    (
        node[amenity]({ax},{ay},{bx},{by});
        node[highway~"bus_stop|crossing|elevator"]({ax},{ay},{bx},{by});
        node[railway~"station|subway_entrance|tram_stop"]({ax},{ay},{bx},{by});
    );
    out;"""
    response = requests.get(OVERPASS_API_URL, params={"data": q})
    data = response.json()
    return data


# from https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
# This returns the NW-corner of the square. Use the function with xtile+1 and/or ytile+1 to get the other corners. With xtile+0.5 & ytile+0.5 it will return the center of the tile.
def num2deg(xtile, ytile, zoom):
    n = 2.0**zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


# replicating https://github.com/mapbox/postgis-vt-util/blob/master/src/TileBBox.sql
def tile_bbox_from_x_y(x, y, zoom=16):
    ax, ay = num2deg(x, y, zoom)
    bx, by = num2deg(x + 1, y + 1, zoom)
    tile_minx = min(ax, bx)
    tile_maxx = max(ax, bx)
    tile_miny = min(ay, by)
    tile_maxy = max(ay, by)
    return (tile_minx, tile_miny, tile_maxx, tile_maxy)
