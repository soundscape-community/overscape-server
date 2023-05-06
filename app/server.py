#!/usr/bin/env python3
import json
from aiohttp import web
from osm_query import ZOOM_DEFAULT
from tile_cache import CachedTile


# based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
async def gentile_async(zoom, x, y):
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": CachedTile(x, y).read(),
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
    tile_data = await gentile_async(zoom, x, y)
    if tile_data == None:
        raise web.HTTPServiceUnavailable()
    else:
        return web.Response(text=tile_data, content_type="application/json")


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(
        [
            web.get(r"/{zoom:\d+}/{x:\d+}/{y:\d+}.json", tile_handler),
        ]
    )
    web.run_app(app)
