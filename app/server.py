#!/usr/bin/env python3
import json
from aiohttp import web
from osm_query import ZOOM_DEFAULT, OverpassClient
from tile_cache import TileCache


# based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
async def gentile_async(zoom, x, y, tile_cache):
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": tile_cache.get(x, y),
        },
        sort_keys=True,
    )


# based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
async def tile_handler(request):
    zoom = request.match_info["zoom"]
    if int(zoom) != ZOOM_DEFAULT:
        raise web.HTTPNotFound()
    x = int(request.match_info["x"])
    y = int(request.match_info["y"])
    tile_data = await gentile_async(zoom, x, y, request.app["tile_cache"])
    if tile_data == None:
        raise web.HTTPServiceUnavailable()
    else:
        return web.Response(text=tile_data, content_type="application/json")


def run_serer(overpass_url, user_agent, cache_dir, cache_days, cache_size):
    app = web.Application()
    overpass_client = OverpassClient(overpass_url, user_agent)
    app["tile_cache"] = TileCache(cache_dir, cache_days, cache_size, overpass_client)
    app.add_routes(
        [
            web.get(r"/{zoom:\d+}/{x:\d+}/{y:\d+}.json", tile_handler),
        ]
    )
    web.run_app(app)
