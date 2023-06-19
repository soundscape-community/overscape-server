#!/usr/bin/env python3
import json
from aiohttp import web
from overpass import ZOOM_DEFAULT, OverpassClient
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration


# based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
@sentry_sdk.trace
async def gentile_async(zoom, x, y, overpass_client):
    response = await overpass_client.query(x, y)
    if response is None:
        return response
    return json.dumps(response, sort_keys=True)


# based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
@sentry_sdk.trace
async def tile_handler(request):
    zoom = request.match_info["zoom"]
    if int(zoom) != ZOOM_DEFAULT:
        raise web.HTTPNotFound()
    x = int(request.match_info["x"])
    y = int(request.match_info["y"])
    tile_data = await gentile_async(zoom, x, y, request.app["overpass_client"])
    if tile_data == None:
        raise web.HTTPServiceUnavailable()
    else:
        return web.Response(text=tile_data, content_type="application/json")


def run_server(
    overpass_url,
    user_agent,
    cache_dir,
    cache_days,
    cache_size,
    port,
    sentry_dsn,
    sentry_tsr,
):
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=sentry_tsr,
        integrations=[
            AioHttpIntegration(),
        ],
    )
    sentry_sdk.set_tag(
        "overpass_url", overpass_url
    )  # Tag all requests for the lifecycle of the app with the overpass URL used
    app = web.Application()
    app["overpass_client"] = OverpassClient(
        overpass_url, user_agent, cache_dir, cache_days, cache_size
    )
    app.add_routes(
        [
            web.get(r"/tiles/{zoom:\d+}/{x:\d+}/{y:\d+}.json", tile_handler),
        ]
    )
    web.run_app(app, port=port)
