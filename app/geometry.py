#!/usr/bin/env python3
"""Assorted methods for dealing with polygons, projections, coordinates, etc.
"""
import math

from shapely import Polygon, MultiPolygon

ZOOM_DEFAULT = 16


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


# code copied from https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Python_Parsing
def parse_poly(lines):
    """Parse an Osmosis polygon filter file.

    Accept a sequence of lines from a polygon file, return a shapely.geometry.MultiPolygon object.

    http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
    """
    in_ring = False
    coords = []

    for index, line in enumerate(lines):
        if index == 0:
            # first line is junk.
            continue

        elif index == 1:
            # second line is the first polygon ring.
            coords.append([[], []])
            ring = coords[-1][0]
            in_ring = True

        elif in_ring and line.strip() == "END":
            # we are at the end of a ring, perhaps with more to come.
            in_ring = False

        elif in_ring:
            # we are in a ring and picking up new coordinates.
            ring.append(list(map(float, line.split())))

        elif not in_ring and line.strip() == "END":
            # we are at the end of the whole polygon.
            break

        elif not in_ring and line.startswith("!"):
            # we are at the start of a polygon part hole.
            coords[-1][1].append([])
            ring = coords[-1][1][-1]
            in_ring = True

        elif not in_ring:
            # we are at the start of a polygon part.
            coords.append([[], []])
            ring = coords[-1][0]
            in_ring = True

    return MultiPolygon(coords)


# based on https://gist.github.com/devdattaT/dd218d1ecdf6100bcf15
def getTileASpolygon(z, y, x):
    ymx, xm = num2deg(x, y, z)
    ym, xmx = num2deg(x + 1, y + 1, z)
    return Polygon([(xm, ym), (xmx, ym), (xmx, ymx), (xm, ymx)])
