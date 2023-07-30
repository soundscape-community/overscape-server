#!/usr/bin/env python3

# aiopg bug workaround from https://github.com/aio-libs/aiopg/issues/837#issuecomment-864899918
import selectors
selectors._PollLikeSelector.modify = selectors._BaseSelectorImpl.modify

import json

import aiopg
from psycopg2.extras import NamedTupleCursor
import sentry_sdk

from cache import CompressedJSONCache
from overpass import ZOOM_DEFAULT


tile_query = """
    SELECT * from soundscape_tile(%(zoom)s, %(tile_x)s, %(tile_y)s)
"""


class PostgisClient:
    """A drop-in replacement for OverpassClient that uses a PostGIS server.
    The server is assumed to already be populated, including having the
    soundscape_tile function installed.
    """
    def __init__(self, server, cache_dir, cache_days, cache_size):
        self.server = server
        self.cache = CompressedJSONCache(cache_dir, cache_days, cache_size)

    @sentry_sdk.trace
    async def query(self, x, y):
        response = await self.cache.get(f"{x}_{y}", lambda: self.uncached_query(x, y))
        return response

    @sentry_sdk.trace
    async def uncached_query(self, x, y):
        try:
            async with aiopg.connect(self.server) as conn:
                async with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    response = await self._gentile_async(cursor, x, y)
                    return response
        except Exception as e:
            print(e)
            raise

    # based on https://github.com/microsoft/soundscape/blob/main/svcs/data/gentiles.py
    async def _gentile_async(self, cursor, x, y, zoom=ZOOM_DEFAULT):
        await cursor.execute(tile_query, {'zoom': int(zoom), 'tile_x': x, 'tile_y': y})
        value = await cursor.fetchall()
        return {
            'type': 'FeatureCollection',
            'features': list(map(lambda x: x._asdict(), value))
        }
