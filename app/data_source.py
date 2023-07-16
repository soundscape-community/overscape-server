#!/usr/bin/env python3

import requests
import yaml

from geometry import parse_poly, getTileASpolygon


def parse_server_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        for item in yaml.safe_load(f):
            url = item["url"]
            bounds = [requests.get(url).body for url in item.get("bounds", [])]
            yield DataSource(url, bounds)


class DataSource:
    def __init__(self, url, bounds):
        self.url = url
        self.bounds = [parse_poly(poly) for poly in bounds]

    def contains(self, zoom, x, y):
        if len(self.bounds) == 0:
            return True  # assume covers entire world

        tile = getTileASpolygon(zoom, y, x)
        for poly in self.bounds:
            if poly.intersects(tile):
                return True

        return False  # no regions contained tile
