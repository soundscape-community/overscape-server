import math
import requests

ZOOM_DEFAULT = 16


class OverpassClient:
    def __init__(self, server, user_agent):
        self.server = server
        self.user_agent = user_agent

    def query(self, x, y):
        coords = tile_bbox_from_x_y(x, y)
        return self.query_coords(*coords)

    def query_coords(self, ax, ay, bx, by):
        # using field selection from https://github.com/microsoft/soundscape/blob/main/svcs/data/soundscape/other/mapping.yml
        # TODO expand matched nodes
        q = f"""[out:json][bbox:{ax},{ay},{bx},{by}];
        (
            node[amenity];
            node[entrance];
            node[highway~"bus_stop|crossing|elevator"];
            node[historic];
            node[indoormark~"beacon"];
            node[leisure];
            node[office];
            node[railway~"station|subway_entrance|tram_stop"];
            node[shop];
            node[tourism];
            node[zoo~"enclosure"];
        );
        out;"""
        # TODO check response
        response = requests.get(
            self.server,
            params={"data": q},
            headers={"User-Agent": self.user_agent},
        )
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
def tile_bbox_from_x_y(x, y, zoom=ZOOM_DEFAULT):
    ax, ay = num2deg(x, y, zoom)
    bx, by = num2deg(x + 1, y + 1, zoom)
    tile_minx = min(ax, bx)
    tile_maxx = max(ax, bx)
    tile_miny = min(ay, by)
    tile_maxy = max(ay, by)
    return (tile_minx, tile_miny, tile_maxx, tile_maxy)
