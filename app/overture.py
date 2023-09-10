#!/usr/bin/env python3

import duckdb
import sentry_sdk

from overpass import tile_bbox_from_x_y


# See examples at https://github.com/OvertureMaps/data/blob/main/README.md
# Also: https://til.simonwillison.net/overture-maps/overture-maps-parquet
tile_query = """
select
  id,
  names,
  categories,
  geometry
from
  read_parquet(%(server_url)r, filename=true, hive_partitioning=1)
where
  bbox.minx > %(min_x)s
  and bbox.maxx < %(max_x)s
  and bbox.miny > %(min_y)s
  and bbox.maxy < %(max_y)s
"""


class OvertureClient:
    """A drop-in replacement for OverpassClient that reads Overture data
    directly from a Parquet file in an S3 bucket using DuckDB.
    """

    def __init__(self, server):
        # e.g. 's3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=places/type=*/*'
        self.server = server
        self.db = duckdb.connect()
        self.db.execute("""
            INSTALL httpfs; LOAD httpfs;
            INSTALL spatial; LOAD spatial;
            SET s3_region='us-west-2';
        """)

    @sentry_sdk.trace
    async def query(self, x, y):
        min_x, min_y, max_x, max_y = tile_bbox_from_x_y(x, y)
        q = tile_query % {
            "server_url": self.server,
            #XXX swapping X/Y here based on what matches expected results 
            "min_x": min_y,
            "max_x": max_y,
            "min_y": min_x,
            "max_y": max_x,
        }

        try:
            cursor = self.db.execute(q)
            # convert to DuckDB spatial data to JSON
            # (https://til.simonwillison.net/overture-maps/overture-maps-parquet#user-content-exporting-the-places-to-sqlite)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            dicts = [dict(zip(columns, row)) for row in rows]
            return dicts
        except Exception as e:
            print(e)
            raise
