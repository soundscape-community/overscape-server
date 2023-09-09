#!/usr/bin/env python3
import json
from urllib.parse import urlparse

from aiohttp import web
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from overpass import ZOOM_DEFAULT, OverpassClient
from overture import OvertureClient
from postgis import PostgisClient

import logging
logger=logging.getLogger(__name__)

# workaround for aiohttp on WIndows (https://stackoverflow.com/a/69195609)
import sys, asyncio
if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
@sentry_sdk.trace
async def gentile_async(zoom, x, y, backend_client):
    response = await backend_client.query(x, y)
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
    try:
        tile_data = await gentile_async(zoom, x, y, request.app["backend_client"])
        if tile_data == None:
            raise web.HTTPServiceUnavailable()
        else:
            return web.Response(text=tile_data, content_type="application/json")
    except:
        logger.error(f"request: {request.rel_url}")


def backend_client(backend_url, user_agent, cache_dir, cache_days, cache_size):
    """Determine which backend to use based on URL format."""
    url_parts = urlparse(backend_url)
    if url_parts.scheme in ('http', 'https'):
       return OverpassClient(
            backend_url, user_agent, cache_dir, cache_days, cache_size
        )
    elif url_parts.scheme in ('postgis', 'postgres'):
        return PostgisClient(backend_url)
    elif url_parts.scheme in ('s3',):
        return OvertureClient(backend_url)
    else:
        raise ValueError("Unrecognized protocol %r" % url_parts.scheme)


def run_server(
    backend_url,
    user_agent,
    cache_dir,
    cache_days,
    cache_size,
    port,
    sentry_dsn,
    sentry_tsr,
):
    sentry_sdk.init(
        dsn=sentry_dsn if sentry_dsn != "none" else "",
        traces_sample_rate=sentry_tsr,
        integrations=[
            AioHttpIntegration(),
        ],
    )
    sentry_sdk.set_tag(
        "backend_url", backend_url
    )  # Tag all requests for the lifecycle of the app with the overpass URL used
    app = web.Application()
    app["backend_client"] =backend_client(
        backend_url, user_agent, cache_dir, cache_days, cache_size)
    app.add_routes(
        [
            web.get(r"/tiles/{zoom:\d+}/{x:\d+}/{y:\d+}.json", tile_handler),
        ]
    )
    web.run_app(app, port=port)
