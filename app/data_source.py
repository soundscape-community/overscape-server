#!/usr/bin/env python3

from geometry import parse_poly, getTileASpolygon


class DataSource:
    def __init__(self, poly):
        self.bounds = parse_poly(poly)

    def contains(self, zoom, x, y):
        tile = getTileASpolygon(zoom, y, x)
        return self.bounds.intersects(tile)


class OverpassDataSource(DataSource):
    pass


class PostGISDataSource(DataSource):
    pass
