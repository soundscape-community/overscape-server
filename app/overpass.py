import json
import logging
from pathlib import Path
import sentry_sdk

import osm2geojson
from shapely.geometry import mapping, Point
import aiohttp
import asyncio

from cache import CompressedJSONCache
from geometry import num2deg, tile_bbox_from_x_y

logger = logging.getLogger(__name__)

# using tag selection from https://github.com/microsoft/soundscape/blob/main/svcs/data/soundscape/other/mapping.yml
with open(Path(__file__).parent / "osm_tags.json") as f:
    PRIMARY_TAGS = json.load(f)


class OverpassClient:
    def __init__(self, servers, user_agent, cache_dir, cache_days, cache_size):
        self.servers = servers
        self.user_agent = user_agent
        self.cache = CompressedJSONCache(cache_dir, cache_days, cache_size)
        self.session = None

    def _choose_server(self, x, y):
        for server in self.server:
            if server.contains(x, y):
                return server.url

    def _build_query(self, x, y):
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
        ax, ay, bx, by = tile_bbox_from_x_y(x, y)
        q = ""
        for tag, values in PRIMARY_TAGS.items():
            if len(values) > 0:
                q += f"nwr[{tag}~'{'|'.join(values)}'];\n"
            else:
                q += f"nwr[{tag}];\n"
        return f"""[out:json][bbox:{ax},{ay},{bx},{by}];
        (
            {q}
        );
        out geom;"""

    @sentry_sdk.trace
    async def _execute_query(self, q, server_url):
        if not self.session:
            self.session = aiohttp.ClientSession()
        try:
            async with self.session.get(
                server_url, params={"data": q}, headers={"User-Agent": self.user_agent}
            ) as response:
                if response.status != 200:
                    logger.warning(f"received {response.status} from {server_url}")
                    return None
                json = await response.json()
                return OverpassResponse(json)
        except Exception as e:
            logger.warning("got exception", exc_info=True)
            sentry_sdk.capture_exception(e)
            return None

    @sentry_sdk.trace
    async def query(self, x, y):
        return await self.cache.get(f"{x}_{y}", lambda: self.uncached_query(x, y))

    @sentry_sdk.trace
    async def uncached_query(self, x, y):
        q = self._build_query(x, y)
        server_url = self._choose_server(x, y)
        overpass_response = await self._execute_query(q, server_url)
        if overpass_response is None:
            return None
        return overpass_response.as_soundscape_geojson()


class OverpassResponse:
    def __init__(self, overpass_json):
        self.overpass_json = overpass_json

        self.geojson = osm2geojson.json2geojson(overpass_json)
        self.shapes_json = osm2geojson.json2shapes(overpass_json)

    def _item_to_soundscape_geojson(self, item):
        """Description of format at
        https://github.com/steinbro/soundscape/blob/main/docs/services/data-plane-schema.md
        """
        # primary tag (at least one should exist, because it was included
        # in the results)
        feature_type, feature_value = [
            (k, v) for (k, v) in item["properties"]["tags"].items() if k in PRIMARY_TAGS
        ][0]

        return {
            "feature_type": feature_type,
            "feature_value": feature_value,
            "geometry": item["geometry"],
            "osm_ids": [item["properties"]["id"]],
            "properties": item["properties"]["tags"],
            "type": "Feature",
        }

    def _compute_intersections(self):
        """Find all points that are shared by more than one road.

        Replicates intersection determination from
        https://github.com/microsoft/soundscape/blob/main/svcs/data/tilefunc.sql#L21
        """
        point_to_osm_ids = {}
        for item in self.shapes_json:
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

    def as_soundscape_geojson(self):
        """Use osm2geojson to handle the nontrivial type coversion from OSM
        nodes/ways/relations to GeoJSON points/polygons/multipolygons/etc.
        """
        # TODO add entrances
        features = list(
            self._item_to_soundscape_geojson(item) for item in self.geojson["features"]
        ) + list(self._compute_intersections())
        return {
            "features": features,
            "type": "FeatureCollection",
        }
