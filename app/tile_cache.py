import gzip
import json
import random
from datetime import datetime, timedelta


class TileCache:
    """Decrease the load on the Overpass server by saving local copies of the
    output.
    """
    def __init__(self, dir, max_days, max_entries, overpass_client):
        self.dir = dir
        self.max_age = timedelta(days=max_days)
        self.max_entries = max_entries
        self.overpass_client = overpass_client

        if not self.dir.exists():
            self.dir.mkdir()

    def evict_if_needed(self):
        # TODO better algorithm than random file
        entries = list(self.dir.iterdir())
        if len(entries) > self.max_entries:
            random.choice(entries).unlink()

    def _should_fetch(self, path):
        return (
            not path.exists()
            or (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime))
            > self.max_age
        )

    def get(self, x, y):
        path = self.dir.joinpath(f"{x}_{y}.json.gz")
        if self._should_fetch(path):
            json_data = self.overpass_client.query(x, y)
            self.evict_if_needed()
            with gzip.open(path, "wt", encoding="ascii") as f:
                json.dump(json_data, f)

        with gzip.open(path, "rb") as f:
            return json.load(f)