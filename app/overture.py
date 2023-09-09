#!/usr/bin/env python3

import duckdb
import sentry_sdk

from overpass import tile_bbox_from_x_y


# See examples at https://github.com/OvertureMaps/data/blob/main/README.md
tile_query = """
SELECT TOP 10 *
  FROM
       OPENROWSET(
           BULK %(server_url)r,
           FORMAT = 'PARQUET'
       )
  WITH
       (
           names VARCHAR(MAX),
           categories VARCHAR(MAX),
           websites VARCHAR(MAX),
           phones VARCHAR(MAX),
           bbox VARCHAR(200),
           geometry VARBINARY(MAX)
       )
    AS
       [result]
 WHERE
       TRY_CONVERT(FLOAT, JSON_VALUE(bbox, '$.minx')) > %(min_x)s
   AND TRY_CONVERT(FLOAT, JSON_VALUE(bbox, '$.maxx')) < %(mix_x)s
   AND TRY_CONVERT(FLOAT, JSON_VALUE(bbox, '$.miny')) > %(min_y)s
   AND TRY_CONVERT(FLOAT, JSON_VALUE(bbox, '$.maxy')) < %(max_y)s
"""


class OvertureClient:
    """A drop-in replacement for OverpassClient that reads Overture data
    directly from a Parquet file in an S3 bucket using DuckDB.
    """

    def __init__(self, server):
        self.server = server

    @sentry_sdk.trace
    async def query(self, x, y):
        min_x, min_y, max_x, max_y = tile_bbox_from_x_y(x, y)
        q = tile_query % {
            "server_url": self.server,
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
        }

        try:
            return duckdb.sql(q)
        except Exception as e:
            print(e)
            raise
