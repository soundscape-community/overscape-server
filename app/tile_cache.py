import gzip
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from osm_query import query, tile_bbox_from_x_y


class CachedTile:
    """Decrease the load on the Overpass server by saving local copies of the
    output.
    """

    dir = Path("_tile_cache")
    max_age = timedelta(days=7)
    max_size = 1e5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.path = self.dir.joinpath(f"{x}_{y}.json.gz")

        if not self.dir.exists():
            self.dir.mkdir()

    def _should_fetch(self):
        return (
            not self.path.exists()
            or (datetime.now() - datetime.fromtimestamp(self.path.stat().st_mtime))
            > self.max_age
        )

    def _evict_if_needed(self):
        # TODO better algorithm than random file
        entries = list(self.dir.iterdir())
        if len(entries) > self.max_size:
            random.choice(entries).unlink()

    def _fetch(self):
        coords = tile_bbox_from_x_y(self.x, self.y)
        json_data = query(*coords)

        self._evict_if_needed()
        with gzip.open(self.path, "wt", encoding="ascii") as f:
            json.dump(json_data, f)

    def read(self):
        if self._should_fetch():
            self._fetch()
        with gzip.open(self.path, "rb") as f:
            return json.load(f)
